#!/usr/bin/env python
import sys

import cfnlint.core


def main():
    exitcode = 0
    for f in sys.argv[1:]:
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
