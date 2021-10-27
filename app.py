#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from flask import Flask
from flask import render_template, request, url_for
from flask_bootstrap import Bootstrap

WORKSPACE = os.getcwd()

app = Flask(
    __name__,
    template_folder=os.path.join(WORKSPACE, 'templates'),
    static_folder=os.path.join(WORKSPACE, 'static')
)

bootstrap = Bootstrap()
bootstrap.init_app(app)

GRAPH_TYPES = ['simple', 'original', 'orig_align', 'refined']

@app.route('/', methods=['GET'])
def main():
    if request.method == 'GET':
        ctx = {}
        data_dir = os.path.join(WORKSPACE, 'data')
        seen = set()
        for fn in os.listdir(data_dir):
            prefix = fn.split('.')[0]
            if prefix in seen: continue
            seen.add(prefix)

        ctx['fn_list'] = list(seen)
        ctx['type_list'] = GRAPH_TYPES
        return render_template('index.html', **ctx)

@app.route('/gen', methods=['GET'])
def generate():
    group_name = request.args.get('groupName')    # data prefix
    type_name = request.args.get('typeName')    # mode of QE (original, refined)
    content_i = int(request.args.get('index', 0))
    if group_name is None or type_name is None:
        return render_template('error.html', err_msg='Please specify group prefix and mode.'), 400
    if type_name not in GRAPH_TYPES:
        return render_template('error.html', err_msg=f'Mode [{type_name}] is not supported.'), 400

    ctx = {}

    def read_fn(fn):
        with open(fn, 'r') as f:
            return [l.strip() for l in f]

    if type_name == 'simple':
        suffixes = ['src', 'mt']
    elif type_name == 'original':
        suffixes = ['src', 'mt', 'source_tags', 'mtword_tags', 'gap_tags']
    elif type_name == 'orig_align':
        suffixes = ['src', 'mt', 'source_tags', 'mtword_tags', 'gap_tags', 'src-mt.align']
    elif type_name == 'refined':
        suffixes = ['src', 'mt', 'refine.source_tags', 'refine.mtword_tags', 'refine.gap_tags',
                    'src-mt.align', 'src-gap.align']
    else:
        raise Exception(f'Invalid type {type_name}')

    files_lines = []
    for suf in suffixes:
        fn = f'{group_name}.{suf}'
        if not os.path.isfile(os.path.join(WORKSPACE, 'data', fn)):
            return render_template('error.html', err_msg=f'Cannot find file [{fn}] in data directory.')
        lines = read_fn(os.path.join(WORKSPACE, 'data', fn))
        files_lines.append(lines)
        if len(lines) != len(files_lines[0]):
            return render_template(f'Number of lines not match in {fn}.')
    std_len = len(files_lines[0])

    if content_i > std_len - 1: content_i = 0
    if content_i < 0: content_i = std_len - 1
    for i, suf in enumerate(suffixes):
        suf = suf.replace('refine.', '').replace('.', '_').replace('-', '_')
        ctx[suf] = files_lines[i][content_i]

    ctx['groupName'] = group_name
    ctx['typeName'] = type_name
    ctx['index'] = content_i
    ctx['indexLength'] = std_len
    return render_template('res.html', **ctx)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)