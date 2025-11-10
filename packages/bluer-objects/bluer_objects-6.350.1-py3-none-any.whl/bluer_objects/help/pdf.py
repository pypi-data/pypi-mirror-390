from typing import List

from bluer_options.terminal import show_usage


def help_convert(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "install,combine,~compress"

    return show_usage(
        [
            "@pdf",
            "convert",
            f"[{options}]",
            "<module-name>",
            "<.,this,this/that.md,this/that.jpg,this/that.pdf>",
            "[-|<object-name>]",
        ],
        "md -> pdf.",
        mono=mono,
    )


help_functions = {
    "convert": help_convert,
}
