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
    """
    A class to hold the branch that repository read and write operations target.
    """

    def __init__(self, c: SCCSConstants) -> None:
        """
        Initialize the target branch with the entered constants and no branch set.
        """

        self.c = c
        self._branch: str | None = None

    def set(self, branch_name: str | None) -> None:
        """
        Set the target branch to the entered branch name.
        """

        self._branch = branch_name

    def get(self) -> str | None:
        """
        Return the target branch name, or None if the target branch is not set.
        """

        return self._branch

    def require(self) -> str:
        """
        Return the target branch name. Raise an SCCSException if the target branch is
        not set.
        """

        if self._branch is None:
            raise exceptions.SCCSException(self.c.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE)
        return self._branch

    def reset(self) -> None:
        """
        Reset the target branch to None.
        """

        self._branch = None


class RepositoryData:
    """
    A class to access repository data, including the repository root, repository paths,
    IO, and branch metadata.
    """

    def __init__(
        self, root: Path, repository_name: str, c: SCCSConstants, target: TargetBranch
    ) -> None:
        """
        Initialize the repository data with the entered root, repository name,
        constants, and target branch.
        """

        self.root = root
        self.repository_name = repository_name
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, repository_name, c, self.target)
        self.io = RepositoryIO(root, repository_name, c, self.target)

    def config_data(self, key: str) -> str:
        """
        Return the configuration value of the entered key. Raise an SCCSException if the
        key is not accepted.
        """

        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.SCCSException(self.c.INVALID_KEY_ERROR_MESSAGE)
        return self.io.read_config()[key]

    def raise_for_commit_identifier_length(self, commit_identifier: str) -> None:
        """
        Validate the entered commit identifier by checking that it is not empty and has
        a valid commit identifier length. Raise an SCCSException if the commit
        identifier is invalid.
        """

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
        """
        Return the full path of the commit file matching the entered commit identifier
        in the entered folder. Raise an SCCSException if the commit identifier is
        invalid, no matching commit file exists, or multiple commit files match.
        """

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
        """
        Return the bytes of the commit file matching the entered commit identifier and
        folder. Raise an SCCSException if the commit identifier is invalid, no matching
        commit file exists, or multiple commit files match.
        """

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
        """
        Return the full commit identifier matching the entered short commit identifier.
        """

        path = self.commit_identifier_to_full_path(
            commit_identifier, self.c.DOCUMENT_DIRECTORY
        )
        return path.stem

    def latest_commit_identifier(self) -> str:
        """
        Return the latest commit identifier of the current branch. Raise an
        SCCSException if the latest commit identifier is missing from the repository
        metadata.
        """

        commit_identifier = self.io.read_history()[self.c.LATEST_COMMIT_DICT_KEY]
        if not commit_identifier:
            raise exceptions.SCCSException(
                self.c.INVALID_COMMIT_HISTORY_DIRECTORY_DATA_ERROR_MESSAGE
            )

        return commit_identifier

    def create_commit_identifier(self, commit_identifier_parts: list[str]) -> str:
        """
        Return the commit identifier created by hashing the entered commit identifier
        parts.
        """

        return hashlib.sha256(
            self.c.PATH_SEPARATOR.join(commit_identifier_parts).encode(self.c.UTF_8)
        ).hexdigest()

    def repository_objects(self) -> list[str]:
        """
        Return the commit identifiers stored in the repository objects directory.
        """

        return list(
            set(
                i.stem
                for i in self.paths.objects_path().rglob(self.c.RGLOB_ALL_FILES_PATTERN)
                if i.is_file()
            )
        )

    def base_repository_url(self) -> str:
        """
        Return the remote repository URL without a trailing path separator.
        """

        return self.config_data(self.c.REMOTE_KEY).rstrip(self.c.PATH_SEPARATOR)

    def current_branch(self) -> str:
        """
        Return the current branch of the repository.
        """

        return self.io.read_current_branch_data_key(self.c.CURRENT_BRANCH_DICT_KEY)

    def branches(self) -> list[str]:
        """
        Return the list of branches in the repository.
        """

        return self.io.read_current_branch_data_key(self.c.BRANCHES_DICT_KEY)


class RepositoryIO:
    """
    A class to read and write the document, metadata, configuration, and commit data of
    a repository.
    """

    def __init__(
        self, root: Path, repository_name: str, c: SCCSConstants, target: TargetBranch
    ) -> None:
        """
        Initialize the repository IO with the entered root, repository name, constants,
        and target branch.
        """

        self.root = root
        self.repository_name = repository_name
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, repository_name, c, self.target)

    def file_bytes(self, path: Path) -> bytes:
        """
        Return the bytes of the file at the entered path.
        """

        with open(path, "rb") as f:
            return f.read()

    def document_bytes(self) -> bytes:
        """
        Return the bytes of the repository document.
        """

        return self.file_bytes(self.paths.document_path())

    def write_document_bytes(self, data: bytes) -> None:
        """
        Write the entered bytes to the repository document.
        """

        with open(self.paths.document_path(), "wb") as f:
            f.write(data)
            f.truncate()

    def read_metadata(self) -> dict[str, Any]:
        """
        Return the repository metadata.
        """

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)

    def write_metadata(self, data: dict[str, Any]) -> None:
        """
        Write the entered repository metadata.
        """

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)
            f.truncate()

    def read_branches_data(self) -> dict[str, Any]:
        """
        Return the branches metadata of the repository.
        """

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.BRANCHES_DICT_KEY]

    def write_branches_data(self, data: dict[str, Any]) -> None:
        """
        Write the entered branches metadata to the repository. Raise an SCCSException if
        the target branch is not set.
        """

        self.target.require()

        full_metadata = self.read_metadata()
        full_metadata[self.c.BRANCHES_DICT_KEY] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_branch_data(self) -> dict[str, Any]:
        """
        Return the metadata of the target branch. Raise an SCCSException if the target
        branch is not set.
        """

        self.target.require()

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.BRANCHES_DICT_KEY][self.target.get()]

    def write_branch_data(self, data: dict[str, Any]) -> None:
        """
        Write the entered metadata to the target branch. Raise an SCCSException if the
        target branch is not set.
        """

        self.target.require()

        full_metadata = self.read_metadata()
        full_metadata.setdefault(self.c.BRANCHES_DICT_KEY, {})[self.target.get()] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_current_branch_data(self) -> dict[str, Any]:
        """
        Return the current branch metadata of the repository.
        """

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.CURRENT_BRANCH_DICT_KEY]

    def read_current_branch_data_key(self, key: str) -> Any:
        """
        Return the current branch metadata value of the entered key.
        """

        return self.read_current_branch_data()[key]

    def write_current_branch_data(self, data: dict[str, Any]) -> None:
        """
        Write the entered current branch metadata to the repository.
        """

        full_metadata = self.read_metadata()
        full_metadata[self.c.CURRENT_BRANCH_DICT_KEY] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_config(self) -> dict[str, str]:
        """
        Return the configuration of the repository.
        """

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f).setdefault(self.c.CONFIG_DICT_KEY, {})

    def write_config(self, data: dict[str, str]) -> None:
        """
        Write the entered configuration to the repository.
        """

        full_metadata = self.read_metadata()
        full_metadata[self.c.CONFIG_DICT_KEY] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_history(self) -> dict[str, Any]:
        """
        Return the commit history of the target branch. Raise an SCCSException if the
        target branch is not set.
        """

        self.target.require()

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.BRANCHES_DICT_KEY][self.target.get()][
                self.c.HISTORY_DICT_KEY
            ]

    def write_history(self, data: dict[str, Any]) -> None:
        """
        Write the entered commit history to the target branch. Raise an SCCSException if
        the target branch is not set.
        """

        self.target.require()

        full_metadata = self.read_metadata()
        full_metadata[self.c.BRANCHES_DICT_KEY][self.target.get()][
            self.c.HISTORY_DICT_KEY
        ] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_log(self) -> dict[str, Any]:
        """
        Return the log of the target branch. Raise an SCCSException if the target branch
        is not set.
        """

        self.target.require()

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.BRANCHES_DICT_KEY][self.target.get()][
                self.c.LOG_DICT_KEY
            ]

    def write_log(self, data: dict[str, Any]) -> None:
        """
        Write the entered log to the target branch. Raise an SCCSException if the target
        branch is not set.
        """

        self.target.require()

        full_metadata = self.read_metadata()
        full_metadata[self.c.BRANCHES_DICT_KEY][self.target.get()][
            self.c.LOG_DICT_KEY
        ] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_byte_hash(self) -> dict[str, str]:
        """
        Return the byte hash data of the target branch. Raise an SCCSException if the
        target branch is not set.
        """

        self.target.require()

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.BRANCHES_DICT_KEY][self.target.get()][
                self.c.BYTE_HASH_DICT_KEY
            ]

    def write_byte_hash(self, data: dict[str, str]) -> None:
        """
        Write the entered byte hash data to the target branch. Raise an SCCSException if
        the target branch is not set.
        """

        self.target.require()

        full_metadata = self.read_metadata()
        full_metadata[self.c.BRANCHES_DICT_KEY][self.target.get()][
            self.c.BYTE_HASH_DICT_KEY
        ] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)
            f.truncate()

    def read_commit_messages(self) -> dict[str, str]:
        """
        Return the commit messages of the repository.
        """

        with open(
            self.paths.metadata_path(),
            "r",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            return json.load(f)[self.c.COMMIT_MESSAGES_DICT_KEY]

    def write_commit_messages(self, data: dict[str, str]) -> None:
        """
        Write the entered commit messages to the repository.
        """

        full_metadata = self.read_metadata()
        full_metadata[self.c.COMMIT_MESSAGES_DICT_KEY] = data

        with open(
            self.paths.metadata_path(),
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            json.dump(full_metadata, f, indent=4)

    def document_html_byte_hash(self) -> str:
        """
        Return the SHA-256 hash of the repository document converted to HTML.
        """

        html = self.document_html()
        return hashlib.sha256(html.encode(self.c.UTF_8)).hexdigest()

    def document_byte_hash(self) -> str:
        """
        Return the SHA-256 hash of the repository document.
        """

        with open(self.paths.document_path(), "rb") as f:
            hasher = hashlib.sha256()
            for i in iter(lambda: f.read(self.c.MAX_FILE_READ_SIZE), b""):
                hasher.update(i)
        return hasher.hexdigest()

    def document_html(self) -> str:
        """
        Return the repository document converted to HTML.
        """

        with open(self.paths.document_path(), "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value

    def create_document_commit(self, commit_identifier: str) -> None:
        """
        Copy the repository document to the document objects directory using the entered
        commit identifier.
        """

        name = Path(commit_identifier).with_suffix(self.c.DOCUMENT_EXTENSION)
        shutil.copy2(
            self.paths.document_path(), self.paths.document_objects_path() / name
        )

    def write_html_commit(self, commit_hash: str, html: str) -> None:
        """
        Write the entered HTML to the HTML and view HTML objects directories using the
        entered commit hash.
        """

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
        """
        Write the entered diff output to the diff output file in the repository root.
        """

        with open(
            self.root / self.c.DIFF_OUTPUT_HTML_FILE,
            "w",
            encoding=self.c.UTF_8,
            newline=self.c.NEWLINE,
        ) as f:
            f.write(diff)
            f.truncate()


class RepositoryPaths:
    """
    A class to resolve the paths of the files and directories within a repository.
    """

    def __init__(
        self, root: Path, repository_name: str, c: SCCSConstants, target: TargetBranch
    ) -> None:
        """
        Initialize the repository paths with the entered root, repository name,
        constants, and target branch.
        """

        self.root = root
        self.repository_name = repository_name
        self.c = c
        self.target = target

    def document_path(self) -> Path:
        """
        Return the path of the repository document.
        """

        return (self.root / self.repository_name).with_suffix(self.c.DOCUMENT_EXTENSION)

    def sccs_path(self) -> Path:
        """
        Return the path of the SCCS directory.
        """

        return self.root / self.c.SCCS_DIRECTORY

    def metadata_path(self) -> Path:
        """
        Return the path of the repository metadata file.
        """

        return self.sccs_path() / self.c.METADATA_JSON

    def objects_path(self) -> Path:
        """
        Return the path of the objects directory.
        """

        return self.sccs_path() / self.c.OBJECTS_DIRECTORY

    def document_objects_path(self) -> Path:
        """
        Return the path of the document objects directory.
        """

        return self.objects_path() / self.c.DOCUMENT_DIRECTORY

    def view_html_objects_path(self) -> Path:
        """
        Return the path of the view HTML objects directory.
        """

        return self.objects_path() / self.c.VIEW_HTML_DIRECTORY

    def html_objects_path(self) -> Path:
        """
        Return the path of the HTML objects directory.
        """

        return self.objects_path() / self.c.HTML_DIRECTORY


class RepositoryStatus:
    """
    A class to inspect the layout and state of a repository, including its branches and
    uncommitted changes.
    """

    def __init__(
        self, root: Path, repository_name: str, c: SCCSConstants, target: TargetBranch
    ) -> None:
        """
        Initialize the repository status with the entered root, repository name,
        constants, and target branch.
        """

        self.root = root
        self.repository_name = repository_name
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, repository_name, c, self.target)
        self.io = RepositoryIO(root, repository_name, c, self.target)

    def validate_repository_layout(self) -> None:
        """
        Validate the repository layout by checking that the expected directories and
        files exist. Raise an SCCSException if a required directory or file is missing.
        """

        dirs = [
            self.paths.view_html_objects_path(),
            self.paths.html_objects_path(),
            self.paths.sccs_path(),
            self.paths.document_objects_path(),
        ]

        files = [self.paths.document_path(), self.paths.metadata_path()]

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
        """
        Return whether the repository document has uncommitted changes.
        """

        latest_commit_identifier = self.io.read_history()[self.c.LATEST_COMMIT_DICT_KEY]
        byte_hash_data = self.io.read_byte_hash()
        latest_byte_hash = byte_hash_data[latest_commit_identifier]

        document_byte_hash = self.io.document_html_byte_hash()

        return latest_byte_hash != document_byte_hash

    def raise_for_uncommitted_changes(self) -> None:
        """
        Raise an SCCSException if the repository has uncommitted changes.
        """

        if self.validate_uncommitted_changes():
            raise exceptions.SCCSException(
                self.c.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
            )

    def branch_exists(self, branch_name: str | None) -> bool:
        """
        Return whether the entered branch exists in the repository.
        """

        if branch_name is None:
            return False
        branches = (
            i.lower()
            for i in self.io.read_current_branch_data()[self.c.BRANCHES_DICT_KEY]
        )
        return branch_name.lower() in branches

    def is_current_branch(self, branch_name: str | None) -> bool:
        """
        Return whether the entered branch is the current branch of the repository.
        """

        if branch_name is None:
            return False
        current_branch = self.io.read_current_branch_data()[
            self.c.CURRENT_BRANCH_DICT_KEY
        ]
        return branch_name.lower() == current_branch.lower()


class RepositoryWrite:
    """
    A class to modify the configuration, branches, and commit data of a repository.
    """

    def __init__(
        self, root: Path, repository_name: str, c: SCCSConstants, target: TargetBranch
    ) -> None:
        """
        Initialize the repository write operations with the entered root, repository
        name, constants, and target branch.
        """

        self.root = root
        self.repository_name = repository_name
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, repository_name, c, self.target)
        self.io = RepositoryIO(root, repository_name, c, self.target)

    def write_key_to_config(
        self, key: str, value: str, current_config: dict[str, str]
    ) -> None:
        """
        Write the entered key-value pair to the repository configuration. Raise an
        SCCSException if the value is empty, contains invalid characters, or the key is
        not accepted.
        """

        if not value or not value.strip():
            raise exceptions.SCCSException(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
            )

        if key in [self.c.NAME_KEY, self.c.EMAIL_KEY] and not all(
            i for i in self.c.ALLOWED_NAME_AND_EMAIL_CHARACTERS for i in value
        ):
            raise exceptions.SCCSException(
                self.c.INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE
            )
        if key == self.c.REMOTE_KEY and not all(
            i for i in self.c.ALLOWED_REMOTE_CHARACTERS for i in value
        ):
            raise exceptions.SCCSException(
                self.c.INVALID_CHARACTER_IN_REMOTE_ERROR_MESSAGE
            )

        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.SCCSException(self.c.INVALID_KEY_ERROR_MESSAGE)

        config = self.io.read_config()
        config[key] = value

        self.io.write_config(config)

    def add_to_branches_list(self, branch_name: str) -> None:
        """
        Add the entered branch to the list of branches in the current branch metadata.
        """

        branch_data = self.io.read_current_branch_data()
        branch_data[self.c.BRANCHES_DICT_KEY].append(branch_name.lower())
        self.io.write_current_branch_data(branch_data)

    def add_branch_metadata(self, branch_name: str, current_branch_name: str) -> None:
        """
        Add the entered branch by copying the current branch metadata, adding the branch
        to the branches list and updated branches, and setting it as the current branch.
        """

        branch_name = branch_name.lower()

        branches_metadata = self.io.read_branches_data()
        current_branch_metadata = branches_metadata[current_branch_name]

        branches_metadata[branch_name] = current_branch_metadata

        self.io.write_branch_data(branches_metadata[branch_name])

        self.add_to_branches_list(branch_name)
        self.add_to_updated_branches(branch_name, current_branch_name)
        self.set_current_branch(branch_name)

    def remove_from_branches_list(self, branch_name: str) -> None:
        """
        Remove the entered branch from the list of branches in the current branch
        metadata. Raise an SCCSException if the branch is not in the branches list.
        """

        lowercase_branch_name = branch_name.lower()

        branch_data = self.io.read_current_branch_data()
        if lowercase_branch_name in branch_data[self.c.BRANCHES_DICT_KEY]:
            branch_data[self.c.BRANCHES_DICT_KEY].remove(lowercase_branch_name)
        else:
            raise exceptions.SCCSException(self.c.INVALID_BRANCH_DATA_ERROR_MESSAGE)
        self.io.write_current_branch_data(branch_data)

    def remove_branch_metadata(
        self, branch_name: str, current_branch_name: str
    ) -> None:
        """
        Remove the entered branch by deleting its metadata, removing it from the
        branches list and updated branches, and setting the main branch as the current
        branch if the removed branch was the current branch.
        """

        branch_name = branch_name.lower()

        branches_metadata = self.io.read_branches_data()
        if branch_name in branches_metadata:
            del branches_metadata[branch_name]
        self.io.write_branches_data(branches_metadata)

        self.remove_from_branches_list(branch_name)
        self.remove_from_updated_branch(branch_name)

        if branch_name == current_branch_name:
            self.set_current_branch(self.c.MAIN_BRANCH_NAME)

    def add_to_updated_branches(
        self, branch_name: str, conditional_branch: str | None = None
    ) -> None:
        """
        Add the entered branch to the updated branches in the current branch metadata
        when the conditional branch is None or is already marked as updated.
        """

        branch_name = branch_name.lower()

        branch_data = self.io.read_current_branch_data()
        if self.c.UPDATED_BRANCHES_DICT_KEY not in branch_data:
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = []
        if (
            conditional_branch in branch_data[self.c.UPDATED_BRANCHES_DICT_KEY]
            or conditional_branch is None
        ):
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY].append(branch_name)
            self.io.write_current_branch_data(branch_data)

    def remove_from_updated_branch(self, branch_name: str) -> None:
        """
        Remove the entered branch from the updated branches in the current branch
        metadata.
        """

        branch_name = branch_name.lower()

        branch_data = self.io.read_current_branch_data()
        if self.c.UPDATED_BRANCHES_DICT_KEY not in branch_data:
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = []
        if branch_name in branch_data[self.c.UPDATED_BRANCHES_DICT_KEY]:
            branch_data[self.c.UPDATED_BRANCHES_DICT_KEY].remove(branch_name)
            self.io.write_current_branch_data(branch_data)

    def set_current_branch(self, branch_name: str) -> None:
        """
        Set the entered branch as the current branch of the repository.
        """

        branch_data = self.io.read_current_branch_data()
        branch_data[self.c.CURRENT_BRANCH_DICT_KEY] = branch_name.lower()
        self.io.write_current_branch_data(branch_data)

    def commit_changes(
        self, commit_message: str, allow_empty_commit: bool = False
    ) -> str:
        """
        Commit the current document to the repository and return the new commit
        identifier. Raise an SCCSException if the target branch is not set or if there
        are no uncommitted changes and empty commits are not allowed.
        """

        self.target.require()

        current_branch = self.io.read_current_branch_data()[
            self.c.CURRENT_BRANCH_DICT_KEY
        ].lower()
        latest_commit_identifier = self.io.read_history()[self.c.LATEST_COMMIT_DICT_KEY]
        byte_hash_data = self.io.read_byte_hash()

        latest_byte_hash = byte_hash_data[latest_commit_identifier]
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

        byte_hash_data = self.io.read_byte_hash()
        byte_hash_data[commit_identifier] = document_byte_hash
        self.io.write_byte_hash(byte_hash_data)

        commit_messages = self.io.read_commit_messages()
        commit_messages[commit_identifier] = commit_message
        self.io.write_commit_messages(commit_messages)

        history = self.io.read_history()
        history[self.c.LATEST_COMMIT_DICT_KEY] = commit_identifier
        history[self.c.LATEST_COMMIT_NUMBER_DICT_KEY] = (
            history[self.c.LATEST_COMMIT_NUMBER_DICT_KEY] + 1
        )
        history[self.c.COMMIT_ORDER_DICT_KEY][
            history[self.c.LATEST_COMMIT_NUMBER_DICT_KEY]
        ] = commit_identifier
        self.io.write_history(history)

        log = self.io.read_log()
        log[commit_identifier] = {
            self.c.TIMESTAMP_DICT_KEY: self.c.PROGRAM_START_TIME,
            self.c.AUTHOR_DICT_KEY: self.c.COMMIT_AUTHOR_TEMPLATE.format(
                name=name, email=email
            ),
            self.c.MESSAGE_DICT_KEY: commit_message,
        }
        self.io.write_log(log)

        current_branch_data = self.io.read_current_branch_data()
        if self.c.UPDATED_BRANCHES_DICT_KEY in current_branch_data and isinstance(
            current_branch_data[self.c.UPDATED_BRANCHES_DICT_KEY], list
        ):
            current_branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = list(
                set(
                    current_branch_data[self.c.UPDATED_BRANCHES_DICT_KEY]
                    + [current_branch]
                )
            )
        else:
            current_branch_data[self.c.UPDATED_BRANCHES_DICT_KEY] = [current_branch]
        self.io.write_current_branch_data(current_branch_data)

        return commit_identifier
