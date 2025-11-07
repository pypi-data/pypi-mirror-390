import os, re
import jinja2
from collections import OrderedDict
import typer
from h2ctypes.common import _CXX2CTYPES

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
)

def get_struct_str(filepath):
    with open(filepath, 'r') as f:
        context = f.read()
    type_defs_pattern = r"typedef\s+(\w+)\s+(\w+)\s*;*"
    type_defs_results = re.findall(type_defs_pattern, context, re.DOTALL)
    type_defs = {}
    for (kind, name) in type_defs_results:
        if kind != 'struct':
            type_defs[name] = kind
    const_pattern = r"const\w+\s+(\w+)\s+(\w+)\s+=\s*(\w+)\s*;"
    const_results = re.findall(const_pattern, context, re.DOTALL)
    const_vals = {}
    for _, k, v in const_results:
        const_vals[k] = v
    pattern = r"(struct|enum)\s+\w+\s*\{.*\}.*;"
    matched = re.search(pattern, context, re.DOTALL)
    if matched:
        context = matched.group()
        context = re.sub(r'/\*.*?\*/', '', context, flags=re.DOTALL)
        context = re.sub(r'//.*$', '', context, flags=re.MULTILINE)
    else:
        context = ''
    return context, type_defs, const_vals

def parse_str2json(context, const_vals, verbose=False):
    structs = {}
    enums = {}
    parsing = None
    parsing_type = None
    parse_end_counter = 1
    name_pattern = re.compile(r'(struct|enum)\s+(\w+)\s*\{*(.*)')
    kv_pattern = re.compile(r'([\w\*]+)\s+([\w\[\]]+)\s*;*')
    for line in context.split('\n'):
        if parse_end_counter == 0:
            parsing = None
            parsing_type = None
        cline = line.strip()
        if verbose:
            print(cline)
        if not cline:
            continue
        if 'struct ' in cline or 'enum ' in cline:
            assert not parsing, f'parsing failed! {cline}'
            parse_end_counter = 1
            matched = name_pattern.search(cline)
            name = matched.group(2)
            parsing = name
            if 'struct ' in cline:
                parsing_type = 'struct'
                structs[parsing] = OrderedDict()
            else:
                parsing_type = 'enum'
                enums[parsing] = OrderedDict()
            if verbose:
                print(f'start parsing {parsing_type}: {name}...')
            cline = matched.group(3)
        cline = cline.strip('{ ')
        if 'union' in cline:
            cline = cline.replace('union', '').strip()
            parse_end_counter += 1
        if not cline:
            continue
        if '}' in cline:
            assert 'struct' not in cline and 'enum' not in cline, cline
            parse_end_counter -= 1
            cline = cline.split('}', 1)[0].strip()
        if not cline:
            continue
        if verbose:
            print(cline)
        if parsing_type == 'struct':
            split_clines = cline.split(';')
            for split_cline in split_clines:
                split_cline = split_cline.strip()
                if not split_cline:
                    continue
                kv_match = kv_pattern.search(split_cline)
                k = kv_match.group(1)
                v = kv_match.group(2)
                length = None
                if '[' in v:
                    v_split = v.split('[')
                    v = v_split[0]
                    length = 1
                    for v_len in v_split[1:]:
                        v_len = v_len.strip('] ')
                        if v_len in const_vals:
                            v_len = const_vals[v_len]
                        length *= int(v_len)
                    print(parsing, k, v, length)
                structs[parsing][v] = { 'type': k, 'length': length }
        else:
            split_clines = cline.split(',')
            for split_cline in split_clines:
                split_cline = split_cline.strip()
                if not split_cline:
                    continue
                if verbose:
                    print(split_cline)
                enums[parsing][split_cline] = {'type': 'enum'} # only record info, enum value is not so import here.
        assert 'struct ' not in cline and 'enum ' not in cline, cline
    return structs, enums

def load_structs(filepaths, verbose=False):
    result_type_defs = {}
    result_const_vals = {}
    struct_contexts = []
    for filepath in filepaths:
        struct_context, type_defs, const_vals = get_struct_str(filepath)
        result_type_defs.update(type_defs)
        result_const_vals.update(const_vals)
        struct_contexts.append(struct_context)
    result_structs = {}
    result_enums = {}
    for struct_context in struct_contexts:
        structs, enums = parse_str2json(struct_context, result_const_vals, verbose=verbose)
        result_structs.update(structs)
        result_enums.update(enums)
    #print('[parsing] done')
    return result_structs, result_enums, result_type_defs

def parse2dict(item, base_infos, ret=OrderedDict()):
    structs, enums, type_defs = base_infos
    for k, k_item in item.items():
        v = k_item['type']
        if v in enums:
            ret[k] = {'type': 'uint32_t', 'length': None}
        elif v in structs:
            ext_ret = parse2dict(structs[v], base_infos)
            ret.update(ext_ret)
        elif v in type_defs:
            ret[k] = {'type': type_defs[v], 'length': None}
        else:
            ret[k] = k_item
    return ret

@app.command()
def dump(dump_structname: str,
        input_header_files: list[str],
        dump_json_path: str = '{dump_structname}.json',
        dump_py_path: str = '{dump_structname}.py',
        noconvert: bool = False,
        pack: int = 8,
        verbose: bool = False,
    ):
    import json
    base_infos = load_structs(input_header_files, verbose=verbose)
    structs, enums, type_defs = base_infos
    return_dict = parse2dict(structs[dump_structname], base_infos)
    if noconvert:
        dump_json_path = dump_json_path.format(**locals())
        with open(dump_json_path, 'w') as f:
            json.dump(return_dict, f, indent=2)
        print(f'[dump] {dump_json_path}')
    else:
        # process ctypes map
        template_path = os.path.join(os.path.dirname(__file__), 'struct.py.j2')
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(template_path)),
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
        )
        template = env.get_template(os.path.basename(template_path))
        res = template.render({
            'struct_name': dump_structname,
            'pack': pack,
            'field_infos': [{'name': k, 'ctypes': _CXX2CTYPES[v['type']], 'length': v['length']} for k, v in return_dict.items()],
        })
        dump_py_path = dump_py_path.format(**locals())
        with open(dump_py_path, 'w') as f:
            f.write(res)
        print(f'[dump] {dump_py_path}')

if __name__ == '__main__':
    app()
