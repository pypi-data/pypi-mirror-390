#!/bin/zsh
set -e

# Load shell configuration to get aliases
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

APP_NAME=axmp-openapi-mcp-server
APP_VERSION=0.1.11

docker build --platform linux/amd64 --tls-verify=false -t localhost/${APP_NAME}:${APP_VERSION} .
docker tag localhost/${APP_NAME}:${APP_VERSION} zcr.cloudzcp.net/cloudzcp/${APP_NAME}:${APP_VERSION}
docker push --tls-verify=false zcr.cloudzcp.net/cloudzcp/${APP_NAME}:${APP_VERSION}
