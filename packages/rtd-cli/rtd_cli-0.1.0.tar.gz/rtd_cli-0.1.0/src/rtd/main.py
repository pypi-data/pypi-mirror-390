import json
import subprocess
from functools import partial
from os import getenv
from os.path import join, expanduser, exists
from sys import stdout, stderr

import click
import requests


URL_BASE = 'https://readthedocs.org/api/v3'
RTD_TOKEN_VAR = 'RTD_TOKEN'

err = partial(print, file=stderr)


def get_token():
    token = getenv(RTD_TOKEN_VAR)
    if token:
        return token
    config_dir = getenv('XDG_CONFIG_HOME', join(expanduser('~'), '.config'))
    rtd_config_dir = join(config_dir, 'rtd-cli')
    token_path = join(rtd_config_dir, 'token')
    if exists(token_path):
        with open(token_path, "r") as f:
            return f.read().strip()

    raise RuntimeError(f"Readthedocs API token not found in ${RTD_TOKEN_VAR} or {token_path}")


@click.group("rtd")
def cli():
    """Simple CLI wrapper for the Readthedocs REST API."""
    pass


@cli.command("api")
@click.option('-b', '--body', help='JSON string to send in the body of a PATCH/POST request; if absent, a GET request is sent')
@click.option('-m', '--method', type=click.Choice(['GET', 'POST', 'PATCH'], case_sensitive=False), help='HTTP method to use; defaults to GET if no body, PATCH if body provided')
@click.option('-u', '--show-updated', is_flag=True, help="After a PATCH/POST request (with -b/--body), send a GET to the same endpoint, to verify the updated state of the resource")
@click.argument("endpoint")
def api(body, method, show_updated, endpoint):
    """Make a request to the Readthedocs REST API.

    RTD API docs: https://docs.readthedocs.io/en/stable/api/v3.html
    """
    token = get_token()
    headers = { 'Authorization': f'token {token}' }
    url = join(URL_BASE, endpoint)

    # Determine method
    if method:
        method = method.upper()
    elif body:
        method = 'PATCH'
    else:
        method = 'GET'

    if method in ['POST', 'PATCH']:
        body_obj = json.loads(body) if body else {}
        if method == 'POST':
            response = requests.post(url, json=body_obj, headers=headers)
        else:
            response = requests.patch(url, json=body_obj, headers=headers)
        response.raise_for_status()
        if response.status_code != 204:
            text = response.text
            err(text)

    if (method in ['POST', 'PATCH'] and show_updated) or method == 'GET':
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        body = response.json()
        json.dump(body, stdout, indent=2)


def patch_cmd(name, obj, docstr):
    def cmd(project, no_show_updated, versions):
        for version in versions:
            body = json.dumps(obj)
            api.callback(body=body, show_updated=not no_show_updated, endpoint=f"projects/{project}/versions/{version}/")

    cmd.__doc__ = docstr

    for deco in [
        cli.command(name),
        click.option('-p', '--project'),
        click.option('-U', '--no-show-updated', is_flag=True),
        click.argument("versions", nargs=-1),
    ]:
        cmd = deco(cmd)


patch_cmd("deactivate", {"active": False}, "Deactivate one or more versions")
patch_cmd("hide", {"hidden": True}, "Hide one or more versions")


@cli.command("build")
@click.option('-v', '--version', default='latest', help='Version slug (default: latest)')
@click.argument("project")
def build(version, project):
    """Trigger a build for a project version."""
    endpoint = f"projects/{project}/versions/{version}/builds/"
    api.callback(body=None, method='POST', show_updated=False, endpoint=endpoint)


@cli.command("logs")
@click.argument("build_id")
def logs(build_id):
    """Get build logs for a specific build ID."""
    token = get_token()
    headers = { 'Authorization': f'token {token}' }
    url = f'https://readthedocs.org/api/v2/build/{build_id}.txt'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.text, file=stdout)


@cli.command("open")
@click.option('-b', '--build', 'build_id', help='Open specific build page')
@click.option('-d', '--docs', is_flag=True, help='Open docs site (not dashboard)')
@click.argument("project")
def open_cmd(build_id, docs, project):
    """Open project page in browser."""
    if build_id:
        url = f'https://app.readthedocs.org/projects/{project}/builds/{build_id}/'
    elif docs:
        url = f'https://{project}.readthedocs.io/'
    else:
        url = f'https://app.readthedocs.org/projects/{project}/builds/'

    err(f"Opening {url}")
    subprocess.run(['open', url])
