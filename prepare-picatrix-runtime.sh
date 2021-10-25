#!/bin/bash
# Initialize Picatrix runtime with right set of Jupyter extensions.

# Exit on error. Append "|| true" if you expect an error.
set -o errexit
# Exit on error inside any functions or subshells.
set -o errtrace
# Do not allow use of undefined vars. Use ${VAR:-} to use an undefined VAR
set -o nounset
# Catch the error in case mysqldump fails (but gzip succeeds) in `mysqldump |gzip`
set -o pipefail

jupyter serverextension enable --py jupyter_http_over_ws
jupyter nbextension enable --py widgetsnbextension --sys-prefix
jupyter contrib nbextension install --user
jupyter nbextensions_configurator enable --user
jupyter nbextension enable --py --user ipyaggrid
