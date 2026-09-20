import sys
from pathlib import Path

from local_sccs import (
    branch,
    clone,
    commit,
    config,
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
    switch,
    utils,
    exceptions,
)

from local_sccs.constants_classes import SCCSConstants, ErrorWrappers
from local_sccs.repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
)

COMMANDS =  {
    SCCSConstants.BRANCH_COMMAND_NAME: branch.main,
    SCCSConstants.CLONE_COMMAND_NAME: clone.main,
    SCCSConstants.COMMIT_COMMAND_NAME: commit.main,
    SCCSConstants.CONFIG_COMMAND_NAME: config.main,
    SCCSConstants.DIFF_COMMAND_NAME: diff.main,
    SCCSConstants.HELP_COMMAND_NAME: help.main,
    SCCSConstants.INIT_COMMAND_NAME: init.main,
    SCCSConstants.LOG_COMMAND_NAME: log.main,
    SCCSConstants.MERGE_COMMAND_NAME: merge.main,
    SCCSConstants.OPEN_COMMAND_NAME: open.main,
    SCCSConstants.PUBLISH_COMMAND_NAME: publish.main,
    SCCSConstants.PULL_COMMAND_NAME: pull.main,
    SCCSConstants.PUSH_COMMAND_NAME: push.main,
    SCCSConstants.RESET_COMMAND_NAME: reset.main,
    SCCSConstants.REVERT_COMMAND_NAME: revert.main,
    SCCSConstants.STATUS_COMMAND_NAME: status.main,
    SCCSConstants.SWITCH_COMMAND_NAME: switch.main
}

def run_command(command: str) -> None:
    if command not in COMMANDS:
        c = SCCSConstants()
        print(c.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=command))
        help.main(c)
        return

    c = SCCSConstants()
    error_wrappers = ErrorWrappers()
    wd = utils.working_directory(c)
    target = TargetBranch(c)
    repository_name = wd.name
    document_path = Path(utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX))
    repository_root = document_path.with_suffix(c.EMPTY_STRING)
    wd_rd = RepositoryData(wd, repository_name, c, target),
    rwd_ri = RepositoryIO(Path.cwd(), repository_name, c, target),
    root_ri = RepositoryIO(repository_root, repository_name, c, target),
    cwd_rp = RepositoryPaths(Path.cwd(), repository_name, c, target),
    wd_rp = RepositoryPaths(wd, repository_name, c, target),
    root_rp = RepositoryPaths(repository_root, repository_name, c, target),
    cwd_rs = RepositoryStatus(Path.cwd(), repository_name, c, target),
    wd_rs = RepositoryStatus(wd, repository_name, c, target),
    root_rs = RepositoryStatus(repository_root, repository_name, c, target),
    cwd_rw = RepositoryWrite(Path.cwd(), repository_name, c, target),
    wd_rw = RepositoryWrite(wd, repository_name, c, target),
    root_rw = RepositoryWrite(repository_root, repository_name, c, target)

    COMMAND_ARGUMENTS = {
        c.BRANCH_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            utils.entered_argument(c, c.SECOND_ARGUMENT_INDEX, raise_on_not_provided=False),
            wd_rd,
            wd_rp,
            wd_rs,
            wd_rw,
        ],
        c.CLONE_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        ],
        c.COMMIT_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            cwd_rs,
            cwd_rw,
        ],
        c.CONFIG_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            utils.entered_argument(c, c.SECOND_ARGUMENT_INDEX),
            wd_rd,
            rwd_ri,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.DIFF_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            rwd_ri,
            cwd_rs,
        ],
        c.HELP_COMMAND_NAME: [
            c,
        ],
        c.INIT_COMMAND_NAME: [
            c,
            document_path,
            root_ri,
            root_rp,
            root_rs,
            root_rw,
        ],
        c.LOG_COMMAND_NAME: [
            c,
            wd_rd,
            rwd_ri,
            cwd_rs,
        ],
        c.MERGE_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            rwd_ri,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.OPEN_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            cwd_rs,
        ],
        c.PUBLISH_COMMAND_NAME: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.PULL_COMMAND_NAME: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
        ],
        c.PUSH_COMMAND_NAME: [
            c,
            wd_rd,
            rwd_ri,
            cwd_rp,
            cwd_rs,
        ],
        c.RESET_COMMAND_NAME: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
        ],
        c.REVERT_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.STATUS_COMMAND_NAME: [
            c,
            wd_rd,
            cwd_rs,
        ],
        c.SWITCH_COMMAND_NAME: [
            c,
            utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
    }    

    try:
        COMMANDS[command](*COMMAND_ARGUMENTS[command])
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

def main() -> None:
    c = SCCSConstants()
    if len(sys.argv) < 2:
        help.main(c)
        return

    run_command(sys.argv[1])

if __name__ == "__main__":
    main()