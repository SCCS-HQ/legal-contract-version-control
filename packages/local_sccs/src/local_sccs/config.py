from urllib.parse import urljoin, urlsplit

from local_sccs import utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
)


def print_config_success_message(c: SCCSConstants, key: str, value: str) -> None:
    """
    Print a success message after a successful configuration operation, including the
    key and value that were set.
    """

    print(c.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def resolve_key_value(
    c: SCCSConstants, repository_name: str, key: str, value: str
) -> str:
    """
    Resolve the value for the given key. If the key is 'remote', it ensures that the
    value is a valid URL and appends the required path ending for the repository. For
    other keys, it simply returns the value.

    If the key is 'remote' and validation fails, it raises an SCCSException with an
    appropriate error message.
    """

    if key not in c.ACCEPTED_CONFIG_KEYS:
        raise SCCSException(c.INVALID_KEY_ERROR_MESSAGE)

    utils.raise_if_empty(c, value.strip(), key)

    if key == c.REMOTE_KEY:
        url = (
            value + c.PATH_SEPARATOR if not value.endswith(c.PATH_SEPARATOR) else value
        )
        parsed_url = urlsplit(url)

        if (
            parsed_url.scheme.lower() not in c.ACCEPTED_SCHEMES
            or not parsed_url.netloc
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise SCCSException(c.INVALID_URL_ERROR_MESSAGE)

        required_path_ending = (
            c.REPOSITORIES_PATH_SEGMENT
            + c.PATH_SEPARATOR
            + repository_name
            + c.PATH_SEPARATOR
        )

        return (
            urljoin(url, required_path_ending)
            if not url.endswith(required_path_ending)
            and (not parsed_url.path or parsed_url.path == c.PATH_SEPARATOR)
            else url
        )

    return value.strip()
    

def main(
    c: SCCSConstants,
    key: str,
    value: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the config command by setting the current branch as the target, validating the
    repository layout, and writing the entered key-value pair to the configuration of a
    copy of the repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    try:
        rs.validate_repository_layout()

        rs.target.set(rd.current_branch())

        resolved_value = resolve_key_value(
            c, rp.repository_name, key, value
        )

        with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:
            staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

            staging_rw.write_key_to_config(key, resolved_value)

        print_config_success_message(c, key, value)
    except SCCSException:
        raise
    except Exception as e:
        raise SCCSException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()
