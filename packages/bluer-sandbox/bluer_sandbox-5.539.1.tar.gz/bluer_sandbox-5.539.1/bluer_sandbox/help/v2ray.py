from typing import List

from bluer_options.terminal import show_usage, xtra


def import_args(
    mono: bool,
    optional: bool = True,
):
    return (
        lambda thing: [
            (
                "[{}]".format(
                    xtra(
                        thing,
                        mono=mono,
                    )
                )
                if optional
                else thing
            )
        ]
    )('"vless://..." | "vmess://..."')


def import_options(mono: bool):
    return "".join(
        [
            "cat",
            xtra(",dryrun,install,", mono=mono),
            "vless | vmess",
        ]
    )


def help_import(
    tokens: List[str],
    mono: bool,
) -> str:
    options = import_options(mono=mono)

    args = import_args(mono=mono, optional=False)

    return show_usage(
        [
            "@v2ray",
            "import",
            f"[{options}]",
        ]
        + args,
        "import v2ray.",
        mono=mono,
    )


def help_install(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@v2ray",
            "install",
        ],
        "install v2ray.",
        mono=mono,
    )


def help_start(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("import,{}".format(import_options(mono=mono)), mono=mono)

    args = import_args(mono=mono)

    return show_usage(
        [
            "@v2ray",
            "start",
            f"[{options}]",
        ]
        + args,
        "start v2ray.",
        mono=mono,
    )


def help_test(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@v2ray",
            "test",
        ],
        "test v2ray.",
        mono=mono,
    )


help_functions = {
    "import": help_import,
    "install": help_install,
    "start": help_start,
    "test": help_test,
}
