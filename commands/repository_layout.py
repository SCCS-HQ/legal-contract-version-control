#!/usr/bin/env python3

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import exceptions
import mammoth
import utils
from constants_classes import SCCSConstants


class TargetBranch:

    def __init__(self, c: SCCSConstants) -> None:

        self.c = c
        self._branch: str | None = None

    def set(self, branch_name: str | None) -> None:

        self._branch = branch_name

    def get(self) -> str | None:

        return self._branch

    def require(self) -> str:

        if self._branch is None:
            raise exceptions.SCCSException(self.c.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE)
        return self._branch

    def reset(self) -> None:

        self._branch = None


class RepositoryData:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:

        self.root = root
        self.repository_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)

    def config_data(self, key: str) -> str:

        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.SCCSException(self.c.INVALID_KEY_ERROR_MESSAGE)
        return self.io.read_config()[key]

    def raise_for_commit_identifier_length(self, commit_identifier: str) -> None:

        if commit_identifier is None:
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=self.c.COMMIT_IDENTIFIER_FIELD_NAME
                )
            )

        if (
            len(commit_identifier) != self.c.FULL_COMMIT_IDENTIFIER_LENGTH
            and len(commit_identifier) != self.c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
        ):
            raise exceptions.SCCSException(
                self.c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE
            )

    def commit_identifier_to_full_path(
        self, commit_identifier: str, folder: str
    ) -> Path:
        if commit_identifier is None:
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=self.c.COMMIT_IDENTIFIER_FIELD_NAME
                )
            )

        if (
            len(commit_identifier) != self.c.FULL_COMMIT_IDENTIFIER_LENGTH
            and len(commit_identifier) != self.c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
        ):
            raise exceptions.SCCSException(
                self.c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE
            )

        matching_files = []

        for i in Path(self.paths.objects_path() / folder).iterdir():
            if str(i.stem).startswith(commit_identifier):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.SCCSException(
                self.c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
                    file_path=commit_identifier
                )
            )

        if len(matching_files) > 1:
            raise exceptions.SCCSException(
                self.c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                    commit_identifier=commit_identifier
                )
            )

        return Path(matching_files[0])

    def commit_file_bytes(self, commit_identifier: str, folder: str) -> bytes:

        if commit_identifier is None:
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=self.c.COMMIT_IDENTIFIER_FIELD_NAME
                )
            )

        if (
            len(commit_identifier) != self.c.FULL_COMMIT_IDENTIFIER_LENGTH
            and len(commit_identifier) != self.c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
        ):
            raise exceptions.SCCSException(
                self.c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE
            )

        matching_files = []

        for i in Path(self.paths.objects_path() / folder).iterdir():
            if str(i.stem).startswith(commit_identifier):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.SCCSException(
                self.c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
                    file_path=commit_identifier
                )
            )

        if len(matching_files) > 1:
            raise exceptions.SCCSException(
                self.c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                    commit_identifier=commit_identifier
                )
            )

        return self.io.file_bytes(matching_files[0])

    def short_commit_identifier_to_full(self, commit_identifier: str) -> str:

        path = self.commit_identifier_to_full_path(
            commit_identifier, self.c.DOCUMENT_DIRECTORY
        )
        return path.stem

    def latest_commit_identifier(self) -> str:

        commit_identifier = self.io.read_history()[self.c.HISTORY_DICT_KEY][
            self.c.LATEST_COMMIT_DICT_KEY
        ]
        if not commit_identifier:
            raise exceptions.SCCSException(
                self.c.INVALID_COMMIT_HISTORY_DIRECTORY_DATA_ERROR_MESSAGE
            )

        return commit_identifier

    def create_commit_identifier(self, commit_identifier_parts: list[str]) -> str:

        return hashlib.sha256(
            self.c.PATH_SEPARATOR.join(commit_identifier_parts).encode(self.c.UTF_8)
        ).hexdigest()

    def repository_objects(self) -> list[str]:

        return list(
            set(
                i.stem
                for i in self.paths.objects_path().rglob(self.c.RGLOB_ALL_FILES_PATTERN)
                if i.is_file()
            )
        )

    def base_repository_url(self) -> str:

        return self.config_data(self.c.REMOTE_KEY).rstrip(self.c.PATH_SEPARATOR)

    def current_branch(self) -> str:

        return self.io.read_current_branch_data_key(self.c.CURRENT_BRANCH_DICT_KEY)

    def branches(self) -> list[str]:

        return self.io.read_current_branch_data_key(self.c.BRANCHES_DICT_KEY)


class RepositoryIO:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:

        self.root = root
        self.repository_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)

    def file_bytes(self, path: Path) -> bytes:

        with open(path, "rb") as f:
            return f.read()

    def document_bytes(self) -> bytes:

        return self.file_bytes(self.paths.document_path())

    def write_document_bytes(self, data: bytes) -> None:

        with open(self.paths.document_path(), "wb") as f:
            f.write(data)

    def read_current_branch_data(self) -> dict[str, Any]:

        with open(
            self.paths.current_branch_data_file_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def read_current_branch_data_key(self, key: str) -> Any:

        return self.read_current_branch_data()[key]

    def write_current_branch_data(self, data: dict[str, Any]) -> None:

        with open(
            self.paths.current_branch_data_file_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)
            f.truncate()

    def read_config(self) -> dict[str, str]:

        with open(
            self.paths.config_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def write_config(self, data: dict[str, str]) -> None:

        with open(
            self.paths.config_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)
            f.truncate()

    def read_history(self) -> dict[str, Any]:

        with open(
            self.paths.history_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def write_history(self, data: dict[str, Any]) -> None:

        with open(
            self.paths.history_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)

    def read_byte_hash(self) -> dict[str, str]:

        with open(
            self.paths.byte_hash_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def write_byte_hash(self, data: dict[str, str]) -> None:

        with open(
            self.paths.byte_hash_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)

    def read_commit_messages(self) -> dict[str, str]:

        with open(
            self.paths.commit_messages_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def write_commit_messages(self, data: dict[str, str]) -> None:

        with open(
            self.paths.commit_messages_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)

    def document_html_byte_hash(self) -> str:

        html = self.document_html()
        return hashlib.sha256(html.encode(self.c.UTF_8)).hexdigest()

    def document_byte_hash(self) -> str:

        with open(self.paths.document_path(), "rb") as f:
            hasher = hashlib.sha256()
            for i in iter(lambda: f.read(self.c.MAX_FILE_READ_SIZE), b""):
                hasher.update(i)
        return hasher.hexdigest()

    def document_html(self) -> str:

        with open(self.paths.document_path(), "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value

    def create_document_commit(self, commit_identifier: str) -> None:

        name = Path(commit_identifier).with_suffix(self.c.DOCUMENT_EXTENSION)
        shutil.copy2(
            self.paths.document_path(), self.paths.document_objects_path() / name
        )

    def write_html_commit(self, commit_hash: str, html: str) -> None:

        name = Path(commit_hash).with_suffix(self.c.HTML_EXTENSION)
        for i in (
            self.paths.html_objects_path(),
            self.paths.view_html_objects_path(),
        ):
            with open(
                i / name,
                "w",
                encoding=self.c.UTF_8,
                newline=self.c.NEWLINE,
            ) as f:
                f.write(utils.wrap_html(self.c, html, self.c.DEFAULT_HTML_STYLES))

    def write_diff_output(self, diff: str) -> None:

        with open(
            self.root / self.c.DIFF_OUTPUT_HTML_FILE,
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            f.write(diff)


class RepositoryPaths:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:

        self.root = root
        self.repository_name = root.stem
        self.c = c
        self.target = target

    def document_path(self) -> Path:

        return (self.root / self.repository_name).with_suffix(self.c.DOCUMENT_EXTENSION)

    def sccs_path(self) -> Path:

        return self.root / self.c.SCCS_DIRECTORY

    def branches_path(self) -> Path:

        return self.sccs_path() / self.c.BRANCHES_DIRECTORY

    def commit_messages_directory_path(self) -> Path:

        return self.sccs_path() / self.c.COMMIT_MESSAGES_DIRECTORY

    def commit_messages_path(self) -> Path:

        return self.commit_messages_directory_path() / self.c.COMMIT_MESSAGES_JSON_FILE

    def config_directory_path(self) -> Path:

        return self.sccs_path() / self.c.CONFIG_DIRECTORY

    def config_path(self) -> Path:

        return self.config_directory_path() / self.c.CONFIG_JSON_FILE

    def current_branch_directory_path(self) -> Path:

        return self.sccs_path() / self.c.CURRENT_BRANCH_DIRECTORY

    def current_branch_data_file_path(self) -> Path:

        return self.current_branch_directory_path() / self.c.CURRENT_BRANCH_JSON_FILE

    def objects_path(self) -> Path:

        return self.sccs_path() / self.c.OBJECTS_DIRECTORY

    def document_objects_path(self) -> Path:

        return self.objects_path() / self.c.DOCUMENT_DIRECTORY

    def view_html_objects_path(self) -> Path:

        return self.objects_path() / self.c.VIEW_HTML_DIRECTORY

    def html_objects_path(self) -> Path:

        return self.objects_path() / self.c.HTML_DIRECTORY

    def history_directory_path(self) -> Path:

        branch = self.target.require()

        return self.branch_path(branch) / self.c.HISTORY_DIRECTORY

    def history_path(self) -> Path:

        return self.history_directory_path() / self.c.HISTORY_JSON_FILE

    def byte_hash_directory_path(self) -> Path:

        branch = self.target.require()

        return self.branch_path(branch) / self.c.COMMIT_BYTE_HASH_DIRECTORY

    def byte_hash_path(self) -> Path:

        return self.byte_hash_directory_path() / self.c.COMMIT_BYTE_HASH_JSON_FILE

    def branch_path(self, branch_name: str) -> Path:

        return self.branches_path() / branch_name


class RepositoryStatus:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:

        self.root = root
        self.repository_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)

    def validate_repository_layout(self) -> None:

        dirs = [
            self.paths.view_html_objects_path(),
            self.paths.html_objects_path(),
            self.paths.sccs_path(),
            self.paths.document_objects_path(),
        ]

        files = [
            self.paths.current_branch_data_file_path(),
            self.paths.commit_messages_path(),
            self.paths.config_path(),
            self.paths.document_path(),
            self.paths.history_path(),
            self.paths.byte_hash_path(),
        ]

        for i in dirs:
            if not i.is_dir():
                raise exceptions.SCCSException(
                    self.c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
                        resource_name=i
                    )
                )
        for i in files:
            if not i.is_file():
                raise exceptions.SCCSException(
                    self.c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
                        resource_name=i
                    )
                )

    def validate_uncommitted_changes(self) -> bool:

        latest_commit_identifier = self.io.read_history()[self.c.HISTORY_DICT_KEY][
            self.c.LATEST_COMMIT_DICT_KEY
        ]
        latest_byte_hash = self.io.read_byte_hash()[latest_commit_identifier]
        document_byte_hash = self.io.document_html_byte_hash()

        return latest_byte_hash != document_byte_hash

    def raise_for_uncommitted_changes(self) -> None:

        if self.validate_uncommitted_changes():
            raise exceptions.SCCSException(
                self.c.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
            )

    def branch_exists(self, branch_name: str | None) -> bool:

        if branch_name is None:
            return False
        branches = self.io.read_current_branch_data()[self.c.BRANCHES_DICT_KEY]
        return branch_name in branches

    def is_current_branch(self, branch_name: str | None) -> bool:

        if branch_name is None:
            return False
        current_branch = self.io.read_current_branch_data()[
            self.c.CURRENT_BRANCH_DICT_KEY
        ]
        return branch_name == current_branch


class RepositoryWrite:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:

        self.root = root
        self.repository_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)

    def write_key_to_config(self, key: str, value: str) -> None:

        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.SCCSException(self.c.INVALID_KEY_ERROR_MESSAGE)
        try:
            config = self.io.read_config()
            config[key] = value
            self.io.write_config(config)
        except Exception as e:
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
            ) from e

    def add_to_branches_list(self, branch_name: str) -> None:

        try:
            branch_data = self.io.read_current_branch_data()
            branch_data[self.c.BRANCHES_DICT_KEY].append(branch_name)
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.SCCSException(
                self.c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                    action=self.c.CREATE_SUBCOMMAND
                )
            ) from e

    def remove_from_branches_list(self, branch_name: str) -> None:

        try:
            branch_data = self.io.read_current_branch_data()
            if branch_name in branch_data[self.c.BRANCHES_DICT_KEY]:
                branch_data[self.c.BRANCHES_DICT_KEY].remove(branch_name)
            else:
                raise exceptions.SCCSException(self.c.INVALID_BRANCH_DATA_ERROR_MESSAGE)
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.SCCSException(
                self.c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                    action=self.c.DELETE_SUBCOMMAND
                )
            ) from e

    def set_current_branch(self, branch_name: str) -> None:

        try:
            branch_data = self.io.read_current_branch_data()
            branch_data[self.c.CURRENT_BRANCH_DICT_KEY] = branch_name
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=self.c.BRANCH_NAME_FIELD_NAME
                )
            ) from e

    def commit_changes(
        self, commit_message: str, allow_empty_commit: bool = False
    ) -> str:

        current_branch = self.io.read_current_branch_data()[
            self.c.CURRENT_BRANCH_DICT_KEY
        ]
        latest_commit_identifier = self.io.read_history()[self.c.HISTORY_DICT_KEY][
            self.c.LATEST_COMMIT_DICT_KEY
        ]
        latest_byte_hash = self.io.read_byte_hash()[latest_commit_identifier]
        document_byte_hash = self.io.document_html_byte_hash()

        if not allow_empty_commit:
            if latest_byte_hash == document_byte_hash:
                raise exceptions.SCCSException(
                    self.c.NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
                )

        config = self.io.read_config()
        name = config[self.c.NAME_KEY]
        email = config[self.c.EMAIL_KEY]

        commit_identifier_parts = [
            self.c.PROGRAM_START_TIME,
            commit_message,
            name,
            email,
        ]
        commit_identifier = hashlib.sha256(
            self.c.PATH_SEPARATOR.join(commit_identifier_parts).encode(self.c.UTF_8)
        ).hexdigest()

        document_as_html = self.io.document_html()

        self.io.create_document_commit(commit_identifier)
        self.io.write_html_commit(commit_identifier, document_as_html)

        commit_byte_hash = self.io.read_byte_hash()
        commit_byte_hash[commit_identifier] = document_byte_hash

        messages = self.io.read_commit_messages()
        messages[commit_identifier] = commit_message

        history = self.io.read_history()
        history[self.c.HISTORY_DICT_KEY][
            self.c.LATEST_COMMIT_DICT_KEY
        ] = commit_identifier
        history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_NUMBER_DICT_KEY] = (
            history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_NUMBER_DICT_KEY] + 1
        )

        latest_commit_number = history[self.c.HISTORY_DICT_KEY][
            self.c.LATEST_COMMIT_NUMBER_DICT_KEY
        ]
        history[self.c.HISTORY_DICT_KEY][self.c.COMMIT_ORDER_DICT_KEY][
            latest_commit_number
        ] = commit_identifier

        history[self.c.LOG_DICT_KEY][commit_identifier] = {
            self.c.TIMESTAMP_DICT_KEY: self.c.PROGRAM_START_TIME,
            self.c.AUTHOR_DICT_KEY: self.c.COMMIT_AUTHOR_TEMPLATE.format(
                name=name, email=email
            ),
            self.c.MESSAGE_DICT_KEY: commit_message,
        }

        branch_data = self.io.read_current_branch_data()
        updated_branch = [current_branch]
        if self.c.UPDATED_BRANCHES_DICT_KEY in branch_data and isinstance(
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY], list
        ):
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = list(
                set(branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] + updated_branch)
            )
        else:
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = updated_branch

        self.io.write_byte_hash(commit_byte_hash)
        self.io.write_commit_messages(messages)
        self.io.write_history(history)
        self.io.write_current_branch_data(branch_data)

        return commit_identifier
