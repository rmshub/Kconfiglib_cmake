
import os
import sys
import tempfile
import argparse
import kconfiglib
import json
from menuconfig import menuconfig
from subprocess import check_output, CalledProcessError

AUTOHEADER_HEADER = """/*
 * Automatically generated file. DO NOT EDIT.
 * Project Configuration Header
 */
#pragma once
"""

CONFIG_HEADER = """#
# Automatically generated file. DO NOT EDIT.
# Project Configuration
#
"""

CONFIG_CMAKE_HEADER = """#
# Automatically generated file. DO NOT EDIT.
# project configuration cmake include file
#
"""


def get_changed_files_list():
    """ Get both modified and added files list """
    try:
        base_dir = check_output(['git', 'diff', '--name-only', 'HEAD'])
    except CalledProcessError:
        raise IOError('This folder not under git revision')
    return base_dir.decode('utf-8').strip()


def write_cmake(config, filename):
    with open(filename, "w") as f:
        write = f.write
        prefix = config.config_prefix

        write(CONFIG_CMAKE_HEADER)

        def write_node(node):
            sym = node.item
            if not isinstance(sym, kconfiglib.Symbol):
                return

            if sym.config_string:
                val = sym.str_value
                if (
                    sym.orig_type in (kconfiglib.BOOL, kconfiglib.TRISTATE)
                    and val == "n"
                ):
                    val = ""  # write unset values as empty variables
                elif sym.orig_type == kconfiglib.STRING:
                    val = kconfiglib.escape(val)
                elif sym.orig_type == kconfiglib.HEX:
                    val = hex(int(val, 16))  # ensure 0x prefix
                write('set({}{} "{}")\n'.format(prefix, sym.name, val))

        for n in config.node_iter():
            write_node(n)


def write_config(config, filename):
    config.write_config(filename)


def write_header(config, filename):
    config.write_autoconf(filename)


def _replace_empty_assignments(path_in, path_out):
    with open(path_in, "r") as f_in, open(path_out, "w") as f_out:
        for line_num, line in enumerate(f_in, start=1):
            line = line.strip()
            if line.endswith("="):
                line += "n"
                print("{}:{} line was updated to {}".format(
                    path_out, line_num, line))
            f_out.write(line)
            f_out.write("\n")


def load_defaultconfigs(defaults, config):

    if len(defaults) > 0:
        # always load defaults first, so any items which are not defined in that config
        # will have the default defined in the defaults file
        for name in defaults:
            print("Loading defaults file %s..." % name)
            if not os.path.exists(name):
                raise RuntimeError("Defaults file not found: %s" % name)
            try:
                with tempfile.NamedTemporaryFile(
                    prefix="kconfgen_tmp", delete=False
                ) as f:
                    temp_file2 = f.name
                _replace_empty_assignments(name, temp_file2)
                config.load_config(temp_file2, replace=False)

                for symbol, value in config.missing_syms:
                    print(
                        f"warning: unknown kconfig symbol '{symbol}' assigned to '{value}' in {name}"
                    )
            finally:
                try:
                    os.remove(temp_file2)
                except OSError:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Config Generation Tool")

    parser.add_argument(
        "--kconfig",
        help="KConfig file with config item definitions",
        required=True
    )

    parser.add_argument(
        "--config",
        help="Project configuration settings", nargs="?",
        default=None
    )

    parser.add_argument(
        "--defaults",
        help="Optional project defaults file, used if --config file doesn't exist. "
        "Multiple files can be specified using multiple --defaults arguments.",
        nargs="?",
        default=[],
        action="append"
    )

    parser.add_argument(
        "--output",
        nargs=2,
        action="append",
        help="Write output file (format and output filename)",
        metavar=("FORMAT", "FILENAME"),
        default=[],
    )

    parser.add_argument(
        "--menuconfig",
        action="store_true",
        help="Launch menuconfig in console"
    )

    parser.add_argument(
        "--env",
        action="append",
        default=[],
        help="Environment to set when evaluating the config file",
        metavar="NAME=VAL",
    )

    parser.add_argument(
        "--env-file",
        type=argparse.FileType("r"),
        help="Optional file to load environment variables from. Contents "
        "should be a JSON object where each key/value pair is a variable.",
    )

    args = parser.parse_args()

    for fmt, filename in args.output:
        if fmt not in OUTPUT_FORMATS.keys():
            print(
                "Format '%s' not recognised. Known formats: %s"
                % (fmt, OUTPUT_FORMATS.keys())
            )
            sys.exit(1)

    try:
        args.env = [
            (name, value) for (name, value) in (e.split("=", 1) for e in args.env)
        ]
    except ValueError:
        print(
            "--env arguments must each contain =. To unset an environment variable, use 'ENV='"
        )
        sys.exit(1)

    if args.env_file is not None:
        env = json.load(args.env_file)
        os.environ.update(env)

    for name, value in args.env:
        os.environ[name] = value

    # delete generated config file if default file changed
    for name in args.defaults:
        if name in get_changed_files_list():
            if os.path.exists(args.config):
                print(f'{name} modiifed and {args.config} is deleted.')
                os.remove(args.config)
                break

    # set Kconfig enviroment variables
    os.environ["KCONFIG_CONFIG_HEADER"] = CONFIG_HEADER
    os.environ["KCONFIG_AUTOHEADER_HEADER"] = AUTOHEADER_HEADER
    if args.config:
        os.environ["KCONFIG_CONFIG"] = args.config

    config = kconfiglib.Kconfig(args.kconfig)
    config.warn_assign_redun = False
    config.warn_assign_override = False

    if len(args.defaults) > 0:
        load_defaultconfigs(args.defaults, config)

    # If config file previously exists, load it
    if args.config and os.path.exists(args.config):
        config.load_config(args.config, replace=False)

    if args.menuconfig:
        menuconfig(config)

    # Output the files specified in the arguments
    for output_type, filename in args.output:
        try:
            output_function = OUTPUT_FORMATS[output_type]
            output_function(config, filename)
        except OSError:
            pass


OUTPUT_FORMATS = {
    "config": write_config,
    "header": write_header,
    "cmake": write_cmake,
}

if __name__ == '__main__':
    main()
