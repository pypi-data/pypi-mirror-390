#! /usr/bin/env bash

function test_bluer_sandbox_v2ray_import() {
    local options=$1

    bluer_sandbox_v2ray_import \
        cat \
        "$BLUER_SANDBOX_V2RAY_TEST_VLESS"
}
