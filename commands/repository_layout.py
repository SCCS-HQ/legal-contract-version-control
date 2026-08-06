#!/usr/bin/env python3
"""Repository layout classes for SCCS."""

import hashlib
import json
from pathlib import Path
from typing import Any, Self

import mammoth
import exceptions
import shutil
import utils
from constants_classes import SCCSConstants


class TargetBranch:
    """Owns the target-branch state and guard logic. Pure: no I/O, no paths."""

    def __init__(self, c: SCCSConstants) -> None:
        self.c = c
        self._branch: str | None = None


    def set(self, branch_name: str | None) -> None:
        """Set the target branch (and expose it as the configured attribute)."""
        self._branch = branch_name


    def get(self) -> str | None:
        """Return the currently-set target branch, or None."""
        return self._branch


    def require(self) -> str:
        """Return the target branch, raising BranchNotSetError if unset."""
        if self._branch is None:
            raise exceptions.BranchNotSetError(
                self.c.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )
        return self._branch


class RepositoryPaths:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:
        self.root = root
        self.repo_name = root.stem
        self.c = c
        self.target = target


    def document_path(self) -> Path:
        """Return the path to the current document."""
        path = (self.root / self.repo_name).with_suffix(self.c.DOCX_EXTENSION)

        return path


    def sccs_path(self) -> Path:
        """Return the path to the '.sccs' folder."""
        path = self.root / self.c.SCCS_DIR

        return path


    def branches_path(self) -> Path:
        """Return the path to the 'branches' folder."""
        path = self.sccs_path() / self.c.BRANCHES_DIR

        return path


    def commit_messages_dir_path(self) -> Path:
        """Return the path to the 'commit_messages' folder."""
        path = self.sccs_path() / self.c.COMMIT_MESSAGES_DIR

        return path


    def commit_messages_path(self) -> Path:
        """Return the path to the 'commit_messages.json' file."""
        path = self.commit_messages_dir_path() / self.c.COMMIT_MESSAGES_JSON_FILE

        return path


    def config_dir_path(self) -> Path:
        """Return the path to the 'config' folder."""
        path = self.sccs_path() / self.c.CONFIG_DIR

        return path


    def config_path(self) -> Path:
        """Return the path to the 'config.json' file."""
        path = self.config_dir_path() / self.c.CONFIG_JSON_FILE

        return path


    def current_branch_dir_path(self) -> Path:
        """Return the path to the 'current_branch' folder."""
        path = self.sccs_path() / self.c.CURRENT_BRANCH_DIR

        return path


    def current_branch_data_file_path(self) -> Path:
        """Return the path to the 'current_branch.json' file."""
        path = self.current_branch_dir_path() / self.c.CURRENT_BRANCH_JSON_FILE

        return path


    def objects_path(self) -> Path:
        """Return the path to the 'objects' folder."""
        path = self.sccs_path() / self.c.OBJECTS_DIR

        return path


    def docx_objects_path(self) -> Path:
        """Return the path to the 'docx' objects folder."""
        path = self.objects_path() / self.c.DOCX_DIR

        return path


    def view_html_objects_path(self) -> Path:
        """Return the path to the 'view_html' objects folder."""
        path = self.objects_path() / self.c.VIEW_HTML_DIR

        return path


    def html_objects_path(self) -> Path:
        """Return the path to the 'html' objects folder."""
        path = self.objects_path() / self.c.HTML_DIR

        return path


    def history_dir_path(self) -> Path:
        """
        Return the path to the 'history' folder for the current branch. Chaining this
        method with a branch method is required.
        """

        branch = self.target.require()

        path = (self.branch_path(branch) / self.c.HISTORY_DIR)
        
        return path


    def history_path(self) -> Path:
        """
        Return the path to the 'history.json' file for the current branch. Chaining this
        method with a branch method is required.
        """

        path = self.history_dir_path() / self.c.HISTORY_JSON_FILE
        
        return path


    def byte_hashes_dir_path(self) -> Path:
        """
        Return the path to the 'commit_file_hash' folder for the current branch.
        Chaining this method with a branch method is required.
        """
        branch = self.target.require()

        path = (self.branch_path(branch) / self.c.COMMIT_FILE_HASH_DIR)
        
        return path


    def byte_hashes_path(self) -> Path:
        """
        Return the path to the 'commit_file_hash.json' file for the current branch.
        Chaining this method with a branch method is required.
        """
        path = self.byte_hashes_dir_path() / self.c.COMMIT_FILE_HASH_JSON_FILE

        return path


    def branch_path(self, branch_name: str) -> Path:
        """Return the path to the specified branch folder."""
        path = self.branches_path() / branch_name

        return path


    def branch(self, branch_name: str | None) -> Self:
        """Branch method to set the target branch to the specified branch name."""
        self.target.set(branch_name)
        return self


class RepositoryIO:
    """Owns all filesystem I/O. Depends only on RepositoryPaths for paths."""
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:
        self.root = root
        self.repo_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)


    def file_bytes(self, path: Path) -> bytes:
        """Return the raw bytes of the file at 'path' (I/O)."""
        with open(path, "rb") as f:
            return f.read()


    def document_bytes(self) -> bytes:
        """Return the raw bytes of the current DOCX document (I/O)."""
        return self.file_bytes(self.paths.document_path())


    def write_document_bytes(self, data: Any) -> None:
        """Write raw bytes 'data' to the current DOCX document (I/O)."""
        with open(self.paths.document_path(), "wb") as f:
            f.write(data)


    def read_current_branch_data(self) -> dict:
        with open(self.paths.current_branch_data_file_path(), "r", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            return json.load(f)


    def read_current_branch_data_key(self, key: str) -> Any:
        return self.read_current_branch_data()[key]


    def write_current_branch_data(self, data: dict) -> None:
        with open(self.paths.current_branch_data_file_path(), "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            json.dump(data, f, indent=4)
            f.truncate()


    def read_config(self) -> dict:
        with open(self.paths.config_path(), "r", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            return json.load(f)


    def write_config(self, data: dict) -> None:
        with open(self.paths.config_path(), "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            json.dump(data, f, indent=4)
            f.truncate()


    def read_history(self) -> dict:
        with open(self.paths.branch(self.target.require()).history_path(), "r", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            return json.load(f)


    def write_history(self, data: dict) -> None:
        with open(self.paths.branch(self.target.require()).history_path(), "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            json.dump(data, f, indent=4)


    def read_byte_hashes(self) -> dict:
        with open(self.paths.branch(self.target.require()).byte_hashes_path(), "r", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            return json.load(f)


    def write_byte_hashes(self, data: dict) -> None:
        with open(self.paths.branch(self.target.require()).byte_hashes_path(), "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            json.dump(data, f, indent=4)


    def read_commit_messages(self) -> dict:
        with open(self.paths.commit_messages_path(), "r", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            return json.load(f)


    def write_commit_messages(self, data: dict) -> None:
        with open(self.paths.commit_messages_path(), "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            json.dump(data, f, indent=4)


    def document_binary_hash(self) -> str:
        with open(self.paths.document_path(), "rb") as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(self.c.MAX_FILE_READ_SIZE), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


    def document_html(self) -> str:
        with open(self.paths.document_path(), "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value


    def copy_document_to_commit(self, commit_hash: str) -> None:
        name = Path(commit_hash).with_suffix(self.c.DOCX_EXTENSION)
        shutil.copy2(self.paths.document_path(), self.paths.docx_objects_path() / name)


    def write_html_commit(self, commit_hash: str, html: str) -> None:
        name = Path(commit_hash).with_suffix(self.c.DOCX_EXTENSION)
        for d in (self.paths.html_objects_path(), self.paths.view_html_objects_path()):
            with open(d / name, "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
                f.write(utils.wrap_html(self.c, html, self.c.DEFAULT_HTML_STYLES))


    def write_diff_output(self, diff: str) -> None:
        with open(self.root / self.c.DIFF_OUTPUT_HTML_FILE, "w", encoding=self.c.UTF_8, newline=self.c.NEWLINE) as f:
            f.write(diff)


class RepositoryData:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:
        self.root = root
        self.repo_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)


    def config_data(self, key: str) -> str:
        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.InvalidArgumentError(
                self.c.INVALID_KEY_ERROR_MESSAGE
            )
        value = self.io.read_config()[key]
        return value


    def raise_for_commit_length(self, commit: str) -> None:
        if commit is None:
            raise exceptions.InvalidArgumentError(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.c.COMMIT_FILE_FIELD_NAME)
            )

        if len(commit) != self.c.FULL_COMMIT_HASH_LENGTH and len(commit) != self.c.COMMIT_HASH_DISPLAY_LENGTH:
            raise exceptions.InvalidArgumentError(
                self.c.INVALID_COMMIT_HASH_ERROR_MESSAGE
            )


    def hash_to_full_path(self, commit: str, folder: str) -> Path:
        if commit is None:
            raise exceptions.InvalidArgumentError(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.c.COMMIT_FILE_FIELD_NAME)
            )

        if len(commit) != self.c.FULL_COMMIT_HASH_LENGTH and len(commit) != self.c.COMMIT_HASH_DISPLAY_LENGTH:
            raise exceptions.InvalidArgumentError(
                self.c.INVALID_COMMIT_HASH_ERROR_MESSAGE
            )

        matching_files = []

        for i in Path(self.paths.objects_path() / folder).iterdir():
            if str(i.stem).startswith(commit):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.InvalidArgumentError(
                self.c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=commit)
            )

        if len(matching_files) > 1:
            raise exceptions.InvalidArgumentError(
                self.c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(commit=commit)
            )

        return Path(matching_files[0])


    def commit_file_bytes(self, commit: str, folder: str) -> bytes:
        if commit is None:
            raise exceptions.InvalidArgumentError(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.c.COMMIT_FILE_FIELD_NAME)
            )

        if len(commit) != self.c.FULL_COMMIT_HASH_LENGTH and len(commit) != self.c.COMMIT_HASH_DISPLAY_LENGTH:
            raise exceptions.InvalidArgumentError(
                self.c.INVALID_COMMIT_HASH_ERROR_MESSAGE
            )

        matching_files = []

        for i in Path(self.paths.objects_path() / folder).iterdir():
            if str(i.stem).startswith(commit):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.InvalidArgumentError(
                self.c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=commit)
            )

        if len(matching_files) > 1:
            raise exceptions.InvalidArgumentError(
                self.c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(commit=commit)
            )

        return self.io.file_bytes(matching_files[0])


    def latest_commit(self) -> str:
        hash = self.io.read_history()[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_DICT_KEY]
        if not hash:
            raise exceptions.InvalidMetadataError(
                self.c.INVALID_COMMIT_HISTORY_DIR_DATA_ERROR_MESSAGE
            )

        return hash


    def create_commit_sha_hash(self, hash_parts: list[str]) -> str:
        return hashlib.sha256(
            self.c.PATH_SEPARATOR.join(hash_parts).encode(self.c.UTF_8)
        ).hexdigest()


    def repo_objects(self) -> list:
        return list(set(i.stem for i in self.paths.objects_path().rglob(self.c.RGLOB_ALL_FILES_PATTERN) if i.is_file()))


    def base_repo_url(self) -> str:
        return self.config_data(self.c.REMOTE_KEY).rstrip(self.c.PATH_SEPARATOR)


    def current_branch(self) -> str:
        return self.io.read_current_branch_data_key(self.c.CURRENT_BRANCH_DICT_KEY)


    def branches(self) -> list:
        return self.io.read_current_branch_data_key(self.c.BRANCHES_DICT_KEY)


class RepositoryWrite:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:
        self.root = root
        self.repo_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)


    def write_key_to_config(self, key: str, value: str) -> None:
        """Write 'key': 'value' to the SCCS config JSON file."""
        if key not in self.c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.InvalidArgumentError(
                self.c.INVALID_KEY_ERROR_MESSAGE
            )

        try:
            config = self.io.read_config()
            config[key] = value
            self.io.write_config(config)
        except Exception as e:
            raise exceptions.UpdatingMetadataError(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
            ) from e


    def add_to_branches_list(self, branch_name: str) -> None:
        """Add a new branch to the current branch data in the 'current_branch.json' file."""
        try:
            branch_data = self.io.read_current_branch_data()
            branch_data[self.c.BRANCHES_DICT_KEY].append(branch_name)
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.BranchCreationError(
                self.c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=self.c.CREATE_SUBCOMMAND)
            ) from e


    def remove_from_branches_list(self, branch_name: str) -> None:
        """Remove a branch from the current branch data in the 'current_branch.json' file."""
        try:
            branch_data = self.io.read_current_branch_data()
            if branch_name in branch_data[self.c.BRANCHES_DICT_KEY]:
                branch_data[self.c.BRANCHES_DICT_KEY].remove(branch_name)
            else:
                raise exceptions.BranchMissingFromMetadataError(
                    self.c.INVALID_BRANCH_DATA_ERROR_MESSAGE
                )
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.BranchDeletionError(
                self.c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=self.c.DELETE_SUBCOMMAND)
            ) from e


    def set_current_branch(self, branch_name: str) -> None:
        """Set the current branch in the 'current_branch.json' file to the specified branch name."""
        try:
            branch_data = self.io.read_current_branch_data()
            branch_data[self.c.CURRENT_BRANCH_DICT_KEY] = branch_name
            self.io.write_current_branch_data(branch_data)
        except Exception as e:
            raise exceptions.UpdatingMetadataError(
                self.c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.c.BRANCH_NAME_FIELD_NAME)
            ) from e


    def commit_changes(self, commit_msg: str) -> str:
        """
        Commit uncommitted changes to the current branch using 'commit_msg' as the
        commit_message.
        """

        current_branch = self.io.read_current_branch_data()[self.c.CURRENT_BRANCH_DICT_KEY]
        latest_commit = self.io.read_history()[self.c.LATEST_COMMIT_DICT_KEY]
        latest_bytes_hash = self.io.read_byte_hashes()[latest_commit]
        document_hash = self.io.document_binary_hash()

        if latest_bytes_hash == document_hash:
            raise exceptions.NoUncommittedChangesError(
                self.c.NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
            )

        config = self.io.read_config()
        name = config[self.c.NAME_KEY]
        email = config[self.c.EMAIL_KEY]

        hash_parts = [self.c.PROGRAM_START_TIME, commit_msg, name, email]
        commit_hash = hashlib.sha256(
            self.c.PATH_SEPARATOR.join(hash_parts).encode(self.c.UTF_8)
        ).hexdigest()

        document_as_html = self.io.document_html()

        self.io.copy_document_to_commit(commit_hash)
        self.io.write_html_commit(commit_hash, document_as_html)

        commit_file_hash = self.io.read_byte_hashes()
        commit_file_hash[commit_hash] = self.io.document_binary_hash()

        messages = self.io.read_commit_messages()
        messages[commit_hash] = commit_msg

        history = self.io.read_history()
        history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_DICT_KEY] = commit_hash
        history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_NUMBER_DICT_KEY] = (
            history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_NUMBER_DICT_KEY] + 1
        )

        latest_commit_number = history[self.c.HISTORY_DICT_KEY][self.c.LATEST_COMMIT_NUMBER_DICT_KEY]
        history[self.c.HISTORY_DICT_KEY][self.c.COMMIT_ORDER_DICT_KEY][latest_commit_number] = commit_hash

        history[self.c.LOG_DICT_KEY][commit_hash] = {
            self.c.TIMESTAMP_DICT_KEY: self.c.PROGRAM_START_TIME,
            self.c.AUTHOR_DICT_KEY: self.c.COMMIT_AUTHOR_TEMPLATE.format(name=name, email=email),
            self.c.MESSAGE_DICT_KEY: commit_msg,
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

        self.io.write_byte_hashes(commit_file_hash)
        self.io.write_commit_messages(messages)
        self.io.write_history(history)
        self.io.write_current_branch_data(branch_data)

        return commit_hash


class RepositoryStatus:
    def __init__(self, root: Path, c: SCCSConstants, target: TargetBranch) -> None:
        self.root = root
        self.repo_name = root.stem
        self.c = c
        self.target = target
        self.paths = RepositoryPaths(root, c, self.target)
        self.io = RepositoryIO(root, c, self.target)


    def check_repository_layout(self) -> None:
        """
        Validate that required SCCS folders, files, and metadata on the current branch exist
        and that the '.sccs' folder has the correct layout.
        """

        dirs = [
            self.paths.view_html_objects_path(),
            self.paths.html_objects_path(),
            self.paths.sccs_path(),
            self.paths.docx_objects_path()
        ]

        files = [
            self.paths.current_branch_data_file_path(),
            self.paths.commit_messages_path(),
            self.paths.config_path(),
            self.paths.document_path(),
            self.paths.history_path(),
            self.paths.byte_hashes_path()
        ]

        for i in dirs:
            if not i.is_dir():
                raise exceptions.InvalidMetadataError(
                    self.c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(resource_name=i)
                )
        for i in files:
            if not i.is_file():
                raise exceptions.InvalidMetadataError(
                    self.c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(resource_name=i)
                )


    def check_for_uncommitted_changes(self) -> bool:
        """
        Check for uncommitted changes by hashing the current document bytes and comparing
        that to the latest commit bytes hash from the SCCS metadata.
        """

        current_branch = self.io.read_current_branch_data()[self.c.CURRENT_BRANCH_DICT_KEY]
        latest_commit = self.io.read_history()[self.c.LATEST_COMMIT_DICT_KEY]
        latest_bytes_hash = self.io.read_byte_hashes()[latest_commit]
        document_hash = self.io.document_binary_hash()

        return latest_bytes_hash != document_hash


    def raise_for_uncommitted_changes(self) -> None:
        """Raise UncommittedChangesError if uncommitted changes exist."""

        if self.check_for_uncommitted_changes():
            raise exceptions.UncommittedChangesError(
                self.c.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
            )


    def branch_exists(self, branch_name: str) -> bool:
        """Return true if 'branch_name' exists in the repository, false if not."""
        branches = self.io.read_current_branch_data()[self.c.BRANCHES_DICT_KEY]
        return branch_name in branches


    def is_current_branch(self, branch_name: str) -> bool:
        """Return true if 'branch_name' is the current branch, false if not."""
        current_branch = self.io.read_current_branch_data()[self.c.CURRENT_BRANCH_DICT_KEY]
        return branch_name == current_branch