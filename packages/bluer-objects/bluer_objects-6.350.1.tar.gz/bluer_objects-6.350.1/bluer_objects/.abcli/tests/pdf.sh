#! /usr/bin/env bash

function test_bluer_objects_pdf_convert() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_objects_pdf_convert \
        install,combine \
        bluer_objects \
        aliases,aliases/assets.md \
        "${@:2}"

    return 0
}
