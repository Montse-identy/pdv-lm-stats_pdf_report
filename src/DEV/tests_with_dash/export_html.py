import os
from html.parser import HTMLParser

import dash
import pandas as pd
import requests

from dash.dependencies import Input, Output
from src.DEV.pages import overview

# Read finger CSV
finger_data = 'data/df_finger_data.csv'
df_finger = pd.read_csv(finger_data)

license_id = 1234
package_id = "finger.identy.io"

def patch_file(file_path: str, content: bytes, extra: dict = None) -> bytes:
    if file_path == 'index.html':
        index_html_content = content.decode('utf8')
        extra_jsons = f'''
        var patched_jsons_content={{
        {','.join(["'/" + k + "':" + v.decode("utf8") + "" for k, v in extra.items()])}
        }};
        '''
        patched_content = index_html_content.replace(
            '<footer>',
            f'''
            <footer>
            <script>
            ''' + extra_jsons + '''
            const origFetch = window.fetch;
            window.fetch = function () {
                const e = arguments[0]
                if (patched_jsons_content.hasOwnProperty(e)) {
                    return Promise.resolve({
                        json: () => Promise.resolve(patched_jsons_content[e]),
                        headers: new Headers({'content-type': 'application/json'}),
                        status: 200,
                    });
                } else {
                    return origFetch.apply(this, arguments)
                }
            }
            </script>
            '''
        ).replace(
            'href="/',
            'href="'
        ).replace(
            'src="/',
            'src="'
        )
        return patched_content.encode('utf8')
    else:
        return content


def write_file(file_path: str, content: bytes, target_dir='target', ):
    target_file_path = os.path.join(target_dir, file_path.lstrip('/').split('?')[0])
    target_leaf_dir = os.path.dirname(target_file_path)
    os.makedirs(target_leaf_dir, exist_ok=True)
    with open(target_file_path, 'wb') as f:
        f.write(content)
    pass


class ExternalResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []

    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            for k, v in attrs:
                if k == 'href':
                    self.resources.append(v)
        if tag == 'script':
            for k, v in attrs:
                if k == 'src':
                    self.resources.append(v)


def make_static(base_url, target_dir='target'):
    index_html_bytes = requests.get(base_url).content
    json_paths = ['_dash-layout', '_dash-dependencies', ]
    extra_json = {}
    for json_path in json_paths:
        json_content = requests.get(base_url + json_path).content
        extra_json[json_path] = json_content

    patched_bytes = patch_file('index.html', index_html_bytes, extra=extra_json)
    write_file('index.html', patched_bytes, target_dir)
    parser = ExternalResourceParser()
    parser.feed(patched_bytes.decode('utf8'))
    extra_js = [
        '_dash-component-suites/dash/dcc/async-graph.js',
        '_dash-component-suites/dash/dcc/async-plotlyjs.js',
        '_dash-component-suites/dash/dash_table/async-table.js',
        '_dash-component-suites/dash/dash_table/async-highlight.js'
    ]
    for resource_url in parser.resources + extra_js:
        resource_url_full = base_url + resource_url
        print(f'get {resource_url_full}')
        resource_bytes = requests.get(resource_url_full).content
        patched_bytes = patch_file(resource_url, resource_bytes)
        write_file(resource_url, patched_bytes, target_dir)


# Dash App
app = dash.Dash(__name__)
app.title = "PRODUCT ACTIVITY OVERVIEW"
server = app.server

# Describe the layout/ UI of the app
'''
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)
'''

app.layout = overview.create_layout(app, license_id, package_id)

'''
# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    return overview.create_layout(app, license_id, package_id)
'''


@app.callback(
    Output('saved', 'children'),
    Input('save', 'n_clicks'),
)
def save_result(n_clicks):
    if n_clicks == 0:
        return 'not saved'
    else:
        make_static('http://127.0.0.1:8050/')
        return 'saved'


if __name__ == "__main__":
    #app.run_server(debug=True)

