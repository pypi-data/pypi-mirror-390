#! /usr/bin/env bash

function bluer_sandbox_v2ray_test() {
    local options=$1

    bluer_ai_eval ,$options \
        curl \
        -I https://google.com \
        --proxy http://127.0.0.1:8080 \
        "${@:2}"
}
