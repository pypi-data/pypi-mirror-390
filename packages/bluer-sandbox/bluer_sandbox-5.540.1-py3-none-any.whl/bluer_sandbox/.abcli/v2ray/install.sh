#! /usr/bin/env bash

function bluer_sandbox_v2ray_install() {
    local options=$1

    local thing
    for thing in v2ray jq; do
        bluer_ai_eval \
            ,$options \
            brew install $thing
        [[ $? -ne 0 ]] && return 1
    done
}
