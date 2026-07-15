#!/usr/bin/env python3
"""Repository layout class for SCCS."""

import datetime
import hashlib
import json
from pathlib import Path

import mammoth
import exceptions
import shutil
import utils
from constants_classes import SCCSConstants


class RepositoryLayout:
    def __init__(self, root: Path, constants: SCCSConstants) -> None:
        self.root = root
        self.repo_name = root.stem
        self.constants = constants

# Return Files or Folder Paths

    def _set_branch_name(self, branch_name: str | None) -> None:
        """Set the branch_name attribute to the specified branch name."""
        setattr(self, self.constants.BRANCH_NAME_REPOSITORY_LAYOUT_ATTRIBUTE, branch_name)


    def document_path(self) -> Path:
        """Return the path to the current document."""
        path = self.root / self.root.name + self.constants.DOCX_EXTENSION
        self._set_branch_name(None)
        return path
    

    def sccs_path(self) -> Path:
        """Return the path to the '.sccs' folder."""
        path = self.root / self.constants.SCCS_DIR
        self._set_branch_name(None)
        return path
    

    def branches_path(self) -> Path:
        """Return the path to the 'branches' folder."""
        path = self.sccs_path() / self.constants.BRANCHES_DIR
        self._set_branch_name(None)
        return path
    

    def commit_messages_path(self) -> Path:
        """Return the path to the 'commit_messages.json' file."""
        path = self.sccs_path() / self.constants.COMMIT_MESSAGES_DIR / self.constants.COMMIT_MESSAGES_JSON_FILE
        self._set_branch_name(None)
        return path
    

    def config_path(self) -> Path:
        """Return the path to the 'config.json' file."""
        path = self.sccs_path() / self.constants.CONFIG_DIR / self.constants.CONFIG_JSON_FILE
        self._set_branch_name(None)
        return path
    

    def current_branch_path(self) -> Path:
        """Return the path to the 'current_branch.json' file."""
        path = self.sccs_path() / self.constants.CURRENT_BRANCH_DIR / self.constants.CURRENT_BRANCH_JSON_FILE
        self._set_branch_name(None)
        return path
    

    def objects_path(self) -> Path:
        """Return the path to the 'objects' folder."""
        path = self.sccs_path() / self.constants.OBJECTS_DIR
        self._set_branch_name(None)
        return path
    

    def docx_objects_path(self) -> Path:
        """Return the path to the 'docx' objects folder."""
        path = self.objects_path() / self.constants.DOCX_DIR
        self._set_branch_name(None)
        return path
    

    def view_html_objects_path(self) -> Path:
        """Return the path to the 'view_html' objects folder."""
        path = self.objects_path() / self.constants.VIEW_HTML_DIR
        self._set_branch_name(None)
        return path
    

    def html_objects_path(self) -> Path:
        """Return the path to the 'html' objects folder."""
        path = self.objects_path() / self.constants.HTML_DIR
        self._set_branch_name(None)
        return path
    

    def history_path(self) -> Path:
        """
        Return the path to the 'history.json' file for the current branch. Chaining this
        method with a branch method is required.
        """
        
        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        path = (self.branch_path(self.branch_name) / self.constants.HISTORY_DIR / self.constants.HISTORY_JSON_FILE)
        self._set_branch_name(None)
        return path


    def byte_hashes_path(self) -> Path:
        """
        Return the path to the 'commit_file_hash.json' file for the current branch. 
        Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        path = (self.branch_path(self.branch_name) / self.constants.COMMIT_FILE_HASH_DIR / self.constants.COMMIT_FILE_HASH_JSON_FILE)
        self._set_branch_name(None)
        return path
    

    def latest_commit_path(self, folder: str) -> Path:
        """
        Return the pathname of the latest commit for the current branch using 'folder' as
        the type of commit requested (html, docx). Chaining this method with a branch
        method is required.
        """

        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        latest_commit = self.current_branch().latest_commit()

        path = self.commit_file(latest_commit, folder)

        self._set_branch_name(None)
        return path


    def branch_path(self, branch_name: str) -> Path:
        """Return the path to the specified branch folder."""
        path = self.branches_path() / branch_name
        self._set_branch_name(None)
        return path
    

# Return Data from Files


    def current_branch_data(self, key: str | None = None) -> dict | str | None:
        """
        Return the current branch data from the 'current_branch.json' file. If 'key' is
        provided, return the value of that key from the current branch data.
        """

        with open(self.current_branch_path(), "r", encoding="utf-8", newline="\n") as f:
            branch_data = json.load(f)
        if key is None:
            self._set_branch_name(None)
            return branch_data
        self._set_branch_name(None)
        return branch_data[key]


    def config_data(self, key: str ) -> str | None:
        """
        Return the value of the specified key from the SCCS config JSON file.
        Valid keys are 'remote', 'name', and 'email'.
        """
        if key not in self.constants.ACCEPTED_KEYS:
            raise exceptions.InvalidArgumentError(
                self.constants.INVALID_KEY_ERROR_MESSAGE
            )
        
        with open(self.config_path(), "r", encoding="utf-8", newline="\n") as f:
            config_data = json.load(f)

        self._set_branch_name(None)
        return config_data[key]
    

    def history_data(self) -> dict:
        """
        Return the history data from the 'history.json' file for the current branch.
        Chaining this method with a branch method is required.
        """

        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        with open(
            self.branch(self.branch_name).history_path()
            , "r", encoding="utf-8", newline="\n"
        ) as f:
            history_data = json.load(f)

        self._set_branch_name(None)
        return history_data
    

    def byte_hashes_data(self) -> dict:
        """
        Return the byte hashes data from the 'commit_file_hash.json' file for the 
        current branch. Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        with open(
            self.branch_path(self.branch_name) /
            self.byte_hashes_path(), encoding="utf-8", newline="\n"
        ) as f:
            byte_hashes_data = json.load(f)

        self._set_branch_name(None)
        return byte_hashes_data


    def commit_file(self, commit: str, folder: str = "html", path: bool = True, file_data: bool = False, hash_10_char: bool = False) -> str | Path:
        if commit is None:
            raise exceptions.InvalidArgumentError(
                self.constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.constants.COMMIT_FILE_FIELD_NAME)
            )
        
        commit = Path(str(commit).strip())

        if len(commit.stem.strip()) != 64 and len(commit.stem.strip()) != 10:
            raise exceptions.InvalidArgumentError(
                self.constants.INVALID_COMMIT_HASH_ERROR_MESSAGE
            )

        matching_files = []

        for i in Path(self.objects_path() / folder).iterdir():

            if str(i.stem).startswith(str(commit.stem.strip())):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.InvalidArgumentError(
                self.constants.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=commit)
            )

        if len(matching_files) > 1:
            raise exceptions.InvalidArgumentError(
                self.constants.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(commit=commit)
            )

        if path:
            self._set_branch_name(None)
            return Path(matching_files[0])

        if file_data:
            with open(matching_files[0], "r", encoding="utf-8", newline="\n") as f:
                commit_file_data = f.read()
            
            self._set_branch_name(None)
            return commit_file_data
        
        if hash_10_char:
            self._set_branch_name(None)
            return matching_files[0].stem[:10]
        



# Return Miscellaneous Data


    def list_branches(self) -> list[str]:
        self._set_branch_name(None)
        return self.current_branch_data()[self.constants.BRANCHES_DICT_KEY]


    def current_branch_name(self) -> str:
        with open(self.current_branch_path(), "r", encoding="utf-8", newline="\n") as f:
            current_branch_data = json.load(f)
        self._set_branch_name(None)
        return current_branch_data[self.constants.CURRENT_BRANCH_DICT_KEY]
    
    
    def latest_commit(self) -> str | None:
        """
        Retrieve the latest commit hash from the commit history of the current branch.
        Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise exceptions.BranchNotSetError(
                self.constants.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE
            )

        hash = self.history_data()[self.constants.HISTORY_DICT_KEY][self.constants.LATEST_COMMIT_DICT_KEY]
        if not hash:
            raise exceptions.InvalidMetadataError(
                self.constants.INVALID_COMMIT_HISTORY_DIR_DATA_ERROR_MESSAGE
            )
        
        self._set_branch_name(None)
        return hash
    

    def create_commit_sha_hash(self, hash_parts: list[str]):

        return hashlib.sha256(
            self.constants.HASH_PARTS_SEPARATOR.join(hash_parts)
        ).hexdigest()


    def repo_objects(self) -> list[Path]:
        objects_dir = self.objects_path()
        objects = list(set(i.stem for i in objects_dir.rglob(self.constants.RGLOB_ALL_FILES_PATTERN) if i.is_file()))
        return objects


# Write Data to Files


    def write_key_to_config(self, key: str, value: str) -> None:
        """Write 'key': 'value' to the SCCS config JSON file."""
        if key not in self.constants.ACCEPTED_KEYS:
            raise exceptions.InvalidArgumentError(
                self.constants.INVALID_KEY_ERROR_MESSAGE
            )

        try:
            with open(self.config_path(), "r+", encoding="utf-8", newline="\n") as f:
                config = json.load(f)
                config[key] = value
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()

            self._set_branch_name(None)
        except Exception as e:
            raise exceptions.UpdatingMetadataError(
                self.constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
            ) from e


    def add_to_branches_list(self, branch_name: str) -> None:
        """Add a new branch to the current branch data in the 'current_branch.json' file."""
        try:
            with open(self.current_branch_path(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                branch_data[self.constants.BRANCHES_DICT_KEY].append(branch_name)
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.BranchCreationError(
                self.constants.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=self.constants.CREATE_SUBCOMMAND)
            ) from e

        self._set_branch_name(None)


    def remove_from_branches_list(self, branch_name: str) -> None:
        """Remove a branch from the current branch data in the 'current_branch.json' file."""
        try:
            with open(self.current_branch_path(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                if branch_name in branch_data[self.constants.BRANCHES_DICT_KEY]:
                    branch_data[self.constants.BRANCHES_DICT_KEY].remove(branch_name)
                else:
                    raise exceptions.BranchMissingFromMetadataError(
                        self.constants.INVALID_BRANCH_DATA_ERROR_MESSAGE
                    )
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.BranchDeletionError(
                self.constants.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=self.constants.DELETE_SUBCOMMAND)
                ) from e

        self._set_branch_name(None)


    def set_current_branch(self, branch_name: str) -> None:
        """Set the current branch in the 'current_branch.json' file to the specified branch name."""
        try:
            with open(self.current_branch_path(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                branch_data[self.constants.CURRENT_BRANCH_DICT_KEY] = branch_name
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.UpdatingMetadataError(
                self.constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=self.constants.BRANCH_NAME_FIELD_NAME)
            ) from e

        self._set_branch_name(None)


    def write_diff_html_file(self, html: str) -> None:
        with open(
            self.constants.DIFF_OUTPUT_HTML_FILE,  "w", encoding="utf-8", newline="\n"
        ) as f:
            f.write(html)


# Set edit branch status


    def branch(self, branch_name: str) -> None:
        """Branch method to set the target branch to the specified branch name."""
        if branch_name not in self.list_branches():
            self._set_branch_name(None)
            raise exceptions.BranchNotFoundError(
                self.constants.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
            )
        self._set_branch_name(branch_name)
        return self


    def current_branch(self) -> None:
        """Branch method to set the target branch to the current branch."""
        self._set_branch_name(self.current_branch_name())
        return self


# Check Document Status


    def check_repository_layout(self) -> None:    
        """
        Validate that required SCCS folders, files, and metadata on the current branch exist
        and that the '.sccs' folder has the correct layout.
        """


        dirs = [
            self.view_html_objects_path(),
            self.html_objects_path(),
            self.sccs_path(),
            self.docx_objects_path()
        ]

        files = [
            self.current_branch_path(),
            self.commit_messages_path(),
            self.config_path(),
            self.document_path(),
            self.current_branch().history_path(),
            self.current_branch().byte_hashes_path()
        ]

        for i in dirs:
            if not i.is_dir():
                raise exceptions.InvalidMetadataError(
                    self.constants.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(resource_name=i)
                )
        for i in files:
            if not i.is_file():
                raise exceptions.InvalidMetadataError(
                    self.constants.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(resource_name=i)
                )

        self._set_branch_name(None)
            

    def check_for_uncommitted_changes(self, raise_on_changes: bool = True) -> None | bool:
        """
        Check for uncommitted changes by hashing the current document bytes and comparing
        that to the latest commit bytes hash from the SCCS metadata.

        'cmd' is the command being run. It is used in the exception message.

        If raise_on_changes is true, raise an UncommittedChangesError if uncommitted changes were found,
        if not return None.

        If 'raise_on_changes' is false and uncommitted changes were found, return True, if not return
        False.

        'exit' defaults to True.
        """

        latest_commit = self.current_branch().latest_commit()
        
        latest_bytes_hash = self.current_branch().byte_hashes_data()[latest_commit]

        has_uncommitted_changes = latest_bytes_hash != self.convert_docx_to_binary_hash()

        if raise_on_changes:
            if has_uncommitted_changes:
                raise exceptions.UncommittedChangesError(
                    self.constants.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
                )

            self._set_branch_name(None)
            return None

        self._set_branch_name(None)
        return has_uncommitted_changes
        

    def branch_exists(self, branch_name: str) -> bool:
        """Return true if 'branch_name' exists in the repository, false if not."""
        exists = branch_name in self.list_branches()
        self._set_branch_name(None)
        return exists


    def is_current_branch(self, branch_name: str) -> bool:
        """Return true if 'branch_name' is the current branch, false if not."""
        is_current = branch_name == self.current_branch_name()
        self._set_branch_name(None)
        return is_current

# Convert Document


    def convert_docx_to_html(self) -> str | None:
        """
        Convert a DOCX document to HTML and return the generated HTML as a string.
        """

        html_data = None

        try:
            with open(self.document_path(), "rb") as f:
                result = mammoth.convert_to_html(f)
                html_data = result.value
        except Exception as e:
            raise exceptions.ConvertingDocumentToHTMLError from e

        self._set_branch_name(None)
        return html_data
        

    def convert_docx_to_binary_hash(self) -> bytes:
        """
        Create and return a SHA-256 hash of the current DOCX file bytes, reading a 64KB
        chunk at a time.
        """
        try:
            with open(self.document_path(), "rb") as f:
                hasher = hashlib.sha256()
                for i in iter(lambda: f.read(self.constants.MAX_FILE_READ_SIZE), b""):
                    hasher.update(i)
                hashed_file = hasher.hexdigest()
        except Exception as e:
            raise exceptions.DocumentHashingError from e

        self._set_branch_name(None)
        return hashed_file
    

# Commit uncommitted changes


    def commit_changes(self, commit_msg: str) -> str:
        """
        Commit uncommitted changes to the current branch using 'commit_msg' as the
        commit_message.
        """

        # ensure that uncommitted changes exist before committing
        if not self.check_for_uncommitted_changes(raise_on_changes=False):
            raise exceptions.NoUncommittedChangesError(
                self.constants.NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE
            )
        
        # generate the SHA256 commit hash
            
        hash_parts = [self.constants.PROGRAM_START_TIME, commit_msg, self.config_data(self.constants.NAME_KEY), self.config_data(self.constants.EMAIL_KEY), self.current_branch().latest_commit()]

        commit_hash = self.create_commit_sha_hash(hash_parts)
        
        # use mammoth + class method to convert document to html
        document_as_html = self.convert_docx_to_html()

        # copy the current version of the document to the commit directories ('docx', 'html', 'view_html')
        # use the html version for commit directories which require it ('html', 'view_html')
        
        docx_commit_filename = commit_hash + self.constants.DOCX_EXTENSION
        
        shutil.copy2(
                    self.document_path(),
                    self.docx_objects_path() / docx_commit_filename,
                )

        with open(
                self.html_objects_path() / docx_commit_filename,
                "w",
                encoding="utf-8",
                newline="\n",
            ) as f:
                f.write(self.constants.DEFAULT_HTML_STYLES + document_as_html)

        with open(
                self.view_html_objects_path() / docx_commit_filename,
                "w",
                encoding="utf-8",
                newline="\n",
            ) as f:
                f.write(utils.wrap_html(document_as_html), self.constants.DEFAULT_HTML_STYLES)

        # update various repository JSON files, update 'update_dict' with the JSON
        try:
            with open(self.current_branch().byte_hashes_path(), "r", encoding="utf-8", newline="\n") as f:
                commit_file_hash = json.load(f)

        except Exception as e:
            raise exceptions.FileOpenError from e

        commit_file_hash[commit_hash] = self.convert_docx_to_binary_hash()

        with open(
            self.commit_messages_path(), "r", encoding="utf-8", newline="\n"
        ) as f:
            try:
                messages = json.load(f)
            except Exception as e:
                raise exceptions.FileOpenError from e

        messages[commit_hash] =commit_msg

        history = self.current_branch().history_data()

        history[self.constants.HISTORY_DICT_KEY][self.constants.LATEST_COMMIT_DICT_KEY] = commit_hash
        history[self.constants.HISTORY_DICT_KEY][self.constants.LATEST_COMMIT_NUMBER_DICT_KEY] = (
            history[self.constants.HISTORY_DICT_KEY][self.constants.LATEST_COMMIT_NUMBER_DICT_KEY] + 1
        )

        latest_commit_number = history[self.constants.HISTORY_DICT_KEY][self.constants.LATEST_COMMIT_NUMBER_DICT_KEY]

        history[self.constants.HISTORY_DICT_KEY][self.constants.COMMIT_ORDER_DICT_KEY][str(latest_commit_number)] = commit_hash

        history[self.constants.LOG_DICT_KEY][commit_hash] = {
            self.constants.TIMESTAMP_DICT_KEY: self.constants.PROGRAM_START_TIME,
            self.constants.AUTHOR_DICT_KEY: " ".join(self.config_data(self.constants.NAME_KEY), self.config_data(self.constants.EMAIL_KEY)),
            self.constants.MESSAGE_DICT_KEY: commit_msg,
        }

        updated_branch = [self.current_branch_name()]            
        branch_data = self.current_branch_data()

        if self.constants.UPDATED_BRANCHES_DICT_KEY in branch_data and isinstance(
            branch_data[self.constants.UPDATED_BRANCHES_DICT_KEY], list
        ):
            branch_data[self.constants.UPDATED_BRANCHES_DICT_KEY] = list(
                set(branch_data[self.constants.UPDATED_BRANCHES_DICT_KEY] + updated_branch)
            )
        else:
            branch_data[self.constants.UPDATED_BRANCHES_DICT_KEY] = updated_branch

        # 'update_dict' is used to ensure that all repository data is updated atomically
        # entires use the format 'Path: JSON'
        update_dict = {
            self.current_branch().byte_hashes_path(): commit_file_hash,
            self.commit_messages_path(): messages,
            self.current_branch().history_path(): history,
            self.current_branch_path(): branch_data,
        }

        for key, value in update_dict.items():
            print(key)
            try:
                with open(
                    Path(key).with_suffix(self.constants.TMP_EXTENSION), "w", encoding="utf-8", newline="\n"
                ) as f:
                    json.dump(value, f)
            except Exception as e:
                raise exceptions.TemporaryFileError from e

        for key, value in update_dict.items():
            try:
                Path(key).with_suffix(self.constants.TMP_EXTENSION).replace(key)
            except Exception as e:
                raise exceptions.TemporaryFileError from e
        

        return commit_hash
 