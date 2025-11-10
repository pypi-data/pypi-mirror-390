#! /usr/bin/env bash

function bluer_sandbox_v2ray_start() {
    local options=$1
    local do_install=$(bluer_ai_option_int "$options" install 0)
    local do_import=$(bluer_ai_option_int "$options" import 0)

    if [[ "$do_import" == 1 ]]; then
        bluer_sandbox_v2ray_import "$@"
        [[ $? -ne 0 ]] && return 1
    fi

    export http_proxy="http://127.0.0.1:8080"
    export https_proxy="http://127.0.0.1:8080"

    sudo v2ray run \
        -config /usr/local/etc/v2ray/config.json

    bluer_ai_log "unsetting proxy settings..."
    unset http_proxy
    unset https_proxy
}
