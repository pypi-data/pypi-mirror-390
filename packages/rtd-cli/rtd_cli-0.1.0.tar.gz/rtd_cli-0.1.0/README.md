# `rtd`: simple [Readthedocs] CLI

## Install
```bash
pip install rtd-cli
# Set this env var, or write the token to ~/.config/rtd-cli/token
 RTD_TOKEN=your_token
```

## Usage
```bash
rtd --help
# Usage: rtd [OPTIONS] COMMAND [ARGS]...
#
#   Simple CLI wrapper for the Readthedocs REST API.
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   api         Make a request to the Readthedocs REST API.
#   build       Trigger a build for a project version.
#   deactivate  Deactivate one or more versions
#   hide        Hide one or more versions
#   logs        Get build logs for a specific build ID.
#   open        Open project page in browser.

rtd api --help
# Usage: rtd api [OPTIONS] ENDPOINT
#
#   Make a request to the Readthedocs REST API.
#
#   RTD API docs: https://docs.readthedocs.io/en/stable/api/v3.html
#
# Options:
#   -b, --body TEXT                 JSON string to send in the body of a PATCH/POST request;
#                                   if absent, a GET request is sent
#   -m, --method [GET|POST|PATCH]   HTTP method to use; defaults to GET if no body,
#                                   PATCH if body provided
#   -u, --show-updated              After a PATCH/POST request (with -b/--body), send a GET
#                                   to the same endpoint, to verify the updated state of the
#                                   resource
#   --help                          Show this message and exit.

rtd build --help
# Usage: rtd build [OPTIONS] PROJECT
#
#   Trigger a build for a project version.
#
# Options:
#   -v, --version TEXT  Version slug (default: latest)
#   --help              Show this message and exit.

rtd logs --help
# Usage: rtd logs BUILD_ID
#
#   Get build logs for a specific build ID.

rtd open --help
# Usage: rtd open [OPTIONS] PROJECT
#
#   Open project page in browser.
#
# Options:
#   -b, --build TEXT  Open specific build page
#   -d, --docs        Open docs site (not dashboard)
#   --help            Show this message and exit.
```

## Examples

List projects:
```bash
rtd api projects
# {
#   "count": …,
#   "next": null,
#   "previous": null,
#   "results": [
#     …
#   ]
# }
```

Trigger a build:
```bash
rtd build your_project
# or specify a version
rtd build your_project -v stable
```

View build logs:
```bash
rtd logs 30253885
```

Open project pages in browser:
```bash
rtd open levanter                    # Opens builds page
rtd open levanter -b 30253885        # Opens specific build
rtd open levanter -d                 # Opens docs site
```

Update project default branch:
```bash
rtd api projects/your_project/ -b '{"default_branch": "main"}' -u
```

Sync versions from repository:
```bash
rtd api projects/your_project/sync-versions/ -m POST
```

Hide all versions except for a specific list:

```bash
project=your_project
keep=(latest 1.11.)  # grep patterns to keep
limit=100

# Exclude `keep` patterns above, when calling `rtd hide` below
grep_args=(-v)
for v in "${keep[@]}"; do
  grep_args+=(-e "$v")
done

rtd api "projects/$project/versions?limit=$limit&active=true&built=true" \
| jq -r '.results[] | select(.hidden | not) | .slug' \
| grep "${grep_args[@]}" \
| xargs rtd hide -p $p
```

[Readthedocs]: https://readthedocs.org
