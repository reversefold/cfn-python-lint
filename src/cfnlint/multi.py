#!/usr/bin/env python
import shlex
import sys

import cfnlint.core


ARGS_PREFIX = 'ARGS='


def main():
    exitcode = 0
    args = []
    for f in sys.argv[1:]:
        if f.startswith(ARGS_PREFIX):
            args = shlex.split(f[len(ARGS_PREFIX):])
            continue
        (args, filename, template, rules, formatter) = cfnlint.core.get_template_args_rules([f])

        new_exitcode = cfnlint.core.run_cli(
            filename, template, rules,
            args.regions,
            args.override_spec, formatter
        )

        if new_exitcode != 0:
            exitcode = new_exitcode
    return exitcode


if __name__ == '__main__':
    sys.exit(main())
