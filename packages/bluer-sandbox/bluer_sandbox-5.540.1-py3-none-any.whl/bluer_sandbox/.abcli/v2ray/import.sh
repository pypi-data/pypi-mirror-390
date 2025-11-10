#! /usr/bin/env bash

function bluer_sandbox_v2ray_import() {
    local options=$1
    local do_cat=$(bluer_ai_option_int "$options" cat 0)
    local do_install=$(bluer_ai_option_int "$options" install 0)
    local vless_type=$(bluer_ai_option_choice "$options" vless,vmess vless)

    local vless=$2
    if [[ -z "$vless" ]]; then
        bluer_ai_log_error "vl/mess not found."
        return 1
    fi

    local object_name=v2ray-import-$(bluer_ai_string_timestamp)
    local object_path=$ABCLI_OBJECT_ROOT/$object_name
    local filename=$object_path/config.json
    bluer_ai_log "importing $vless_type to $filename..."

    mkdir -pv $object_path

    local repo_path=$abcli_path_git/v2ray-uri2json
    if [[ ! -d "$repo_path" ]]; then
        bluer_ai_git_clone \
            https://github.com/ImanSeyed/v2ray-uri2json.git
        [[ $? -ne 0 ]] && return 1
    fi

    pushd $abcli_path_git/v2ray-uri2json >/dev/null
    [[ $? -ne 0 ]] && return 1

    [[ -f "./config.json" ]] &&
        rm -v ./config.json

    bash \
        scripts/${vless_type}2json.sh \
        "$vless"
    [[ $? -ne 0 ]] && return 1

    mv -v ./config.json \
        $ABCLI_OBJECT_ROOT/$object_name/config.json
    [[ $? -ne 0 ]] && return 1

    popd >/dev/null

    python3 -m bluer_sandbox.v2ray \
        complete_import \
        --object_name $object_name
    [[ $? -ne 0 ]] && return 1

    sudo mkdir -pv /usr/local/etc/v2ray
    sudo cp -v \
        $filename \
        /usr/local/etc/v2ray/config.json
    [[ $? -ne 0 ]] && return 1

    [[ "$do_cat" == 1 ]] &&
        bluer_ai_cat $filename

    if [[ "$do_install" == 1 ]]; then
        bluer_sandbox_v2ray_install "$@"
    fi
}
