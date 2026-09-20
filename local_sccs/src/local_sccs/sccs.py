import sys

from local_sccs import (
    switch
)
from local_sccs import (
    branch, 
    clone,
    commit,
    config,
    constants_classes,
    diff,
    help,
    init,
    log,
    merge,
    open,
    publish,
    pull,
    push,
    reset,
    revert,
    status,
    exceptions
)

COMMANDS =  {
    "branch": branch.main,
    "clone": clone.main,
    "commit": commit.main,
    "config": config.main,
    "diff": diff.main,
    "help": help.main,
    "init": init.main,
    "log": log.main,
    "merge": merge.main,
    "open": open.main,
    "publish": publish.main,
    "pull": pull.main,
    "push": push.main,
    "reset": reset.main,
    "revert": revert.main,
    "status": status.main,
    "switch": switch.main
}

def main() -> None:
    c = constants_classes.SCCSConstants()
    error_wrappers = constants_classes.ErrorWrappers()
    if len(sys.argv) < 2:
        help.main(c)
        return

    command = sys.argv[1]
    if command not in COMMANDS:
        print(c.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=command))
        help.main(c)
        return

    try:
        COMMANDS[command]()
    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(c.EXPECTED_ERROR_EXIT_CODE)

    except Exception as e:
        print(
            error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
                type_name=type(e).__name__, e=e
            )
        )
        sys.exit(c.UNEXPECTED_ERROR_EXIT_CODE)

if __name__ == "__main__":
    main()