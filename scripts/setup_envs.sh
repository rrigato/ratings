#enables all variables defined in .env to be exported
set -o allexport
source .vscode/.env
#disables exporting variables defined in script
set +o allexport