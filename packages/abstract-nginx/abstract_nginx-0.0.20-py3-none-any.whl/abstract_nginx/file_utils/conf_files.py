import os
from abstract_utilities import *
from abstract_utilities.file_utils import *

def get_create_nginx(filename,ext):
    contents=f"""
# HTTP redirect to HTTPS
server *&
    listen 80;
    server_name {filename}{ext} www.{filename}{ext};
    return 301 https://^*host^*request_uri;
&*

# HTTPS server
server *&
    listen 443 ssl http2;
    server_name {filename}{ext} www.{filename}{ext};

    root /var/www/sites/{filename}/html;
    index index.html index.htm;

    ssl_certificate /etc/letsencrypt/live/{filename}{ext}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{filename}{ext}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
&*
"""
    contents=replace_all(contents,["*&","{"],["&*","}"],['^*','$'])
    print(f"contents == {contents}")
    return contents

SITES_AVAILABLE_PATH = "/etc/nginx/sites-available/"

def get_sites_available_item(item):
    return item if SITES_AVAILABLE_PATH in item else None


def get_shortest_path(items):
    shortest = None
    for item in items:
        parts_len = len(item.split('/'))
        if shortest is None or parts_len < len(shortest.split('/')):
            shortest = item
    return shortest


def find_in_sites_available(filename=None,**kwargs):
    dirs, files = get_files_and_dirs(SITES_AVAILABLE_PATH,**kwargs)
    dirs=dirs.split('/n')
    files=files.split('/n')
    matches = [di for di in dirs + files if get_sites_available_item(di) and filename in di]
    if not matches:
        return None
    shortest_match = get_shortest_path(matches)
    shortest_dir = shortest_match if is_dir(shortest_match,**kwargs) else os.path.dirname(shortest_match)
    possible_files = []
    dirs, files = get_files_and_dirs(shortest_dir,**kwargs)
    for file in files:
        dirname = os.path.dirname(file)
        basename = os.path.basename(file)
        if filename in basename and dirname == shortest_dir:
            possible_files.append(file)

    return get_shortest_path(possible_files) if possible_files else shortest_match


def get_content(content=None, file_path=None,**kwargs):
    if content:
        return content
    file_path = eatAll(file_path, [' ', '\t', '', '\n', ';'])
    if file_path and is_file(file_path,**kwargs):
        return read_from_file(file_path,**kwargs)
    return ""


def clean_includes(content=None, file_path=None,**kwargs):
    content = get_content(content=content, file_path=file_path,**kwargs)
    return replace_all(content, ['include  ', 'include '])


def get_lines(content=None, file_path=None,**kwargs):
    content = get_content(content=content, file_path=file_path,**kwargs)
    content = clean_includes(content=content, file_path=file_path,**kwargs)
    return content.split('\n') or []


def get_include_line(line):
    line = eatAll(line, [' ', '\t', ''])
    if line.startswith('include '):
        return line.split('include ')[-1].split(';')[0].strip()
    return None


def resolve_include_path(include_path, base_path=None):
    if not base_path or os.path.isabs(include_path):
        return include_path
    return os.path.normpath(os.path.join(os.path.dirname(base_path), include_path))


def get_includes(content=None, file_path=None, _visited=None,**kwargs):
    _visited = _visited or set()
    lines = get_lines(content=content, file_path=file_path,**kwargs)
    resolved_lines = [f"# {file_path};"] if file_path else []

    for line in lines:
        include_target = get_include_line(line)
        if include_target:
            include_path = resolve_include_path(include_target, base_path=file_path)
            if include_path not in _visited and is_file(include_path,**kwargs):
                _visited.add(include_path)
                included_content = get_includes(
                    file_path=include_path,
                    _visited=_visited,
                    **kwargs
                )
                if isinstance(included_content, list):
                    included_content = '\n'.join(included_content)
                resolved_lines.append(included_content)
            else:
                resolved_lines.append(f"# Skipped include: {include_target}")
        else:
            resolved_lines.append(line)
    return resolved_lines


def format_nginx_content(lines):
    """Cleans up semicolons, tabs, and indents blocks nicely."""
    formatted = []
    indent = 0
    for raw_line in lines.split('\n'):
        line = eatAll(raw_line, [' ', '\t', ''])
        if not line or line.startswith('#'):
            formatted.append(raw_line)
            continue

        # Adjust indentation when a block closes
        if line.startswith('}'):
            indent = max(indent - 1, 0)

        formatted.append('\t' * indent + line.rstrip(';') + (';' if not line.endswith('}') and not line.endswith('{') else ''))

        # Increase indentation after an opening brace
        if line.endswith('{'):
            indent += 1

    return '\n'.join(formatted)


def get_full_confs(filename=None, file_path=None,**kwargs):
    file_path = file_path or find_in_sites_available(filename=filename,**kwargs)
    if not file_path:
        return f"# No config found for {filename}"

    lines = get_includes(file_path=file_path,**kwargs)
    content = '\n'.join(lines)
    clean_content = replace_all(content, [';;', '; ;'], [';', ';'])
    formatted = format_nginx_content(clean_content)
    return formatted



