#!/bin/zsh
set -e

# Load shell configuration to get aliases
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
elif [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

APP_NAME=axmp-openapi-mcp-server
APP_VERSION=0.1.12

docker run --rm -d \
    -v $(pwd)/mcp_profiles:/profiles/mcp_profiles \
    -e AXMP_MCP_PROFILE_BASE_PATH=/profiles/mcp_profiles \
    -e AXMP_MCP_PROFILE_ID=683734a65b3c20f3b1a4f721 \
    -e AXMP_MCP_SERVER_NAME=zcp-alert-backend \
    -e AXMP_MCP_TRANSPORT_TYPE=streamable-http \
    -e AXMP_MCP_PORT=21000 \
    --tls-verify=false \
    zcr.cloudzcp.net/cloudzcp/${APP_NAME}:${APP_VERSION}