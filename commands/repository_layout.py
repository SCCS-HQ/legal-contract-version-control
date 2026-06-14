import datetime
import hashlib
import json
from pathlib import Path

import mammoth
import exceptions
import shutil
import utils

PROGRAM_START_TIME = datetime.datetime.now().isoformat()

class RepositoryLayout:


    def __init__(self, root: Path):
        self.root = root


# Return Files or Folder Paths


    def document_path(self) -> Path:
        """Return the path to the current document."""
        path = self.root / f"{self.root.name}.docx"
        setattr(self, "branch_name", None)
        return path
    

    def sccs_path(self) -> Path:
        """Return the path to the '.sccs' folder."""
        path = self.root / ".sccs"
        setattr(self, "branch_name", None)
        return path
    

    def branches_path(self) -> Path:
        """Return the path to the 'branches' folder."""
        path = self.sccs_path() / "branches"
        setattr(self, "branch_name", None)
        return path
    

    def commit_messages_path(self) -> Path:
        """Return the path to the 'commit_messages.json' file."""
        path = self.sccs_path() / "commit_messages" / "commit_messages.json"
        setattr(self, "branch_name", None)
        return path
    

    def config_path(self) -> Path:
        """Return the path to the 'config.json' file."""
        path = self.sccs_path() / "config" / "config.json"
        setattr(self, "branch_name", None)
        return path
    

    def current_branch_name(self) -> Path:
        """Return the path to the 'current_branch.json' file."""
        path = self.sccs_path() / "current_branch" / "current_branch.json"
        setattr(self, "branch_name", None)
        return path
    

    def objects_path(self) -> Path:
        """Return the path to the 'objects' folder."""
        path = self.sccs_path() / "objects"
        setattr(self, "branch_name", None)
        return path
    

    def docx_objects_path(self) -> Path:
        """Return the path to the 'docx' objects folder."""
        path = self.objects_path() / "docx"
        setattr(self, "branch_name", None)
        return path
    

    def view_html_objects_path(self) -> Path:
        """Return the path to the 'view_html' objects folder."""
        path = self.objects_path() / "view_html"
        setattr(self, "branch_name", None)
        return path
    

    def html_objects_path(self) -> Path:
        """Return the path to the 'html' objects folder."""
        path = self.objects_path() / "html"
        setattr(self, "branch_name", None)
        return path
    

    def history_path(self) -> Path:
        """
        Return the path to the 'history.json' file for the current branch. Chaining this
        method with a branch method is required.
        """
        
        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling history_path(). For example,"
                "'repo_layout.main_branch().history_path()'."
            )

        path = self.branches_path() / self.branch_name / "history" / "history.json"
        setattr(self, "branch_name", None)
        return path


    def byte_hashes_path(self) -> Path:
        """
        Return the path to the 'commit_files_hash.json' file for the current branch. 
        Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling byte_hashes_path(). For example,"
                "'repo_layout.main_branch().byte_hashes_path()'."
            )

        path = self.branches_path() / self.branch_name / "commit_files_hash" / "commit_files_hash.json"
        setattr(self, "branch_name", None)
        return path


    def commit_path(
        self,
        folder: str,
        commit: Path | None = None,
    ) -> Path:
        """
        Convert a commit SHA Hash to a pathname of the specified commit using folder as the
        type of commit requested (html, docx).

        Return the full pathname of the commit using the SHA Hash.
        """

        if commit is None:
            raise exceptions.InvalidArgumentError(
                "No commit file path provided. Please specify a commit file path."
            )
        
        commit = Path(str(commit).strip())

        if len(commit.stem.strip()) != 64 and len(commit.stem.strip()) != 10:
            raise exceptions.InvalidArgumentError(
                "Invalid commit file name. Please provide a shortened, 10 character commit "
                "hash or the full 64 character commit hash as the commit identifier."
            )

        matching_files = []

        for i in Path(self.objects_path() / folder).iterdir():

            if str(i.stem).startswith(str(commit.stem.strip())):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.InvalidArgumentError(
                f"Commit file '{commit}' does not exist. Please provide a valid commit file"
                f" path."
            )

        if len(matching_files) > 1:
            raise exceptions.InvalidArgumentError(
                f"Multiple commit files found matching '{commit}'. Please provide a full, "
                f"64 character commit hash."
            )

        setattr(self, "branch_name", None)
        return matching_files[0]


    def latest_commit_path(self, folder: str) -> Path:
        """
        Return the pathname of the latest commit for the current branch using 'folder' as
        the type of commit requested (html, docx). Chaining this method with a branch
        method is required.
        """

        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling latest_commit_path(). For example,"
                "'repo_layout.main_branch().latest_commit_path()'."
            )

        latest_commit = self.current_branch().latest_commit()

        path = self.commit_path(folder, latest_commit)

        setattr(self, "branch_name", None)
        return path


    def branch_path(self) -> Path:
        """Return the path to the specified branch folder."""
        path = self.branches_path() / self.branch_name
        setattr(self, "branch_name", None)
        return path

# Return Data from Files


    def current_branch_data(self, key: str | None = None) -> dict | str | None:
        """
        Return the current branch data from the 'current_branch.json' file. If 'key' is
        provided, return the value of that key from the current branch data.
        """

        with open(self.current_branch_name(), "r", encoding="utf-8", newline="\n") as f:
            branch_data = json.load(f)
        if key is None:
            setattr(self, "branch_name", None)
            return branch_data
        setattr(self, "branch_name", None)
        return branch_data.get(key)


    def config_data(self, key: str ) -> str | None:
        """
        Return the value of the specified key from the SCCS config JSON file.
        Valid keys are 'remote', 'name', and 'email'.
        """
        if key not in ["remote", "name", "email"]:
            raise exceptions.InvalidArgumentError(
                f"Invalid config key '{key}'. Valid keys are 'remote', 'name', and "
                f"'email'."
            )
        
        with open(self.config_path(), "r", encoding="utf-8", newline="\n") as f:
            config_data = json.load(f)

        setattr(self, "branch_name", None)
        return config_data.get(key)
    

    def history_data(self) -> dict:
        """
        Return the history data from the 'history.json' file for the current branch.
        Chaining this method with a branch method is required.
        """

        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling history_data(). For example,"
                "'repo_layout.main_branch().history_data()'."
            )

        with open(
            self.branches_path() /
            self.branch_name /
            "history" /
            "history.json", "r", encoding="utf-8", newline="\n"
        ) as f:
            history_data = json.load(f)

        setattr(self, "branch_name", None)
        return history_data
    

    def byte_hashes_data(self) -> dict:
        """
        Return the byte hashes data from the 'commit_files_hash.json' file for the 
        current branch. Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling byte_hashes_data(). For example,"
                "'repo_layout.main_branch().byte_hashes_data()'."
            )

        with open(
            self.branches_path() /
            self.branch_name /
            "commit_files_hash" /
            "commit_files_hash.json", "r", encoding="utf-8", newline="\n"
        ) as f:
            byte_hashes_data = json.load(f)

        setattr(self, "branch_name", None)
        return byte_hashes_data


    def commit_file(self, folder: str, commit: str) -> str:
        if commit is None:
            raise exceptions.InvalidArgumentError(
                "No commit file path provided. Please specify a commit file path."
            )
        
        commit = Path(str(commit).strip())

        if len(commit.stem.strip()) != 64 and len(commit.stem.strip()) != 10:
            raise exceptions.InvalidArgumentError(
                "Invalid commit file name. Please provide a shortened, 10 character commit "
                "hash or the full 64 character commit hash as the commit identifier."
            )

        matching_files = []

        for i in Path(self.objects_path() / folder).iterdir():

            if str(i.stem).startswith(str(commit.stem.strip())):
                matching_files.append(i)

        if not matching_files:
            raise exceptions.InvalidArgumentError(
                f"Commit file '{commit}' does not exist. Please provide a valid commit file"
                f" path."
            )

        if len(matching_files) > 1:
            raise exceptions.InvalidArgumentError(
                f"Multiple commit files found matching '{commit}'. Please provide a full, "
                f"64 character commit hash."
            )

        with open(matching_files[0], "r", encoding="utf-8", newline="\n") as f:
            commit_file_data = f.read()
        
        
        setattr(self, "branch_name", None)
        return commit_file_data


# Return Miscellaneous Data


    def list_branches(self) -> list[str]:
        setattr(self, "branch_name", None)
        return [self.branches]


    def current_branch_name(self) -> str:
        with open(self.current_branch_name(), "r", encoding="utf-8", newline="\n") as f:
            current_branch_data = json.load(f)
        setattr(self, "branch_name", None)
        return current_branch_data["current_branch"]
    
    
    def latest_commit(self) -> str | None:
        """
        Retrieve the latest commit hash from the commit history of the current branch.
        Chaining this method with a branch method is required.
        """
        if self.branch_name is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling get_latest_commit(). For example,"
                "'repo_layout.main_branch().get_latest_commit()'."
            )

        hash = self.history_data()["history"].get("latest_commit")

        if not hash:
            raise exceptions.InvalidMetadataError(
                "Latest commit not found in history data. Please ensure the commit data"
                " has not been manually modified"
            )
        
        setattr(self, "branch_name", None)
        return hash
    

# Write Data to Files


    def write_key_to_config(self, key: str, value: str) -> None:
        """Write 'key': 'value' to the SCCS config JSON file."""
        if key not in ["remote", "name", "email"]:
            raise exceptions.InvalidArgumentError(
                f"Invalid config key '{key}'. Valid keys are 'remote', 'name', and "
                f"'email'."
            )


        with open(self.config_path(), "r+", encoding="utf-8", newline="\n") as f:
            config = json.load(f)
            config[key] = value
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()

        setattr(self, "branch_name", None)


    def add_to_branches_list(self, branch_name: str) -> None:
        """Add a new branch to the current branch data in the 'current_branch.json' file."""
        try:
            with open(self.current_branch_name(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                branch_data["branches"].append(branch_name)
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.BranchCreationError from e

        setattr(self, "branch_name", None)


    def remove_from_branches_list(self, branch_name: str) -> None:
        """Remove a branch from the current branch data in the 'current_branch.json' file."""
        try:
            with open(self.current_branch_name(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                if branch_name in branch_data["branches"]:
                    branch_data["branches"].remove(branch_name)
                else:
                    raise exceptions.BranchMissingFromMetadataError(
                        f"Branch '{branch_name}' not found in current branch data."
                    )
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.BranchDeletionError from e

        setattr(self, "branch_name", None)


    def set_current_branch(self, branch_name: str) -> None:
        """Set the current branch in the 'current_branch.json' file to the specified branch name."""
        try:
            with open(self.current_branch_name(), "r+", encoding="utf-8", newline="\n") as f:
                branch_data = json.load(f)
                branch_data["current_branch"] = branch_name
                f.seek(0)
                json.dump(branch_data, f, indent=4)
                f.truncate()

        except Exception as e:
            raise exceptions.UpdatingMetadataError from e

        setattr(self, "branch_name", None)


# Set edit branch status


    def branch(self, branch_name: str) -> None:
        """Branch method to set the target branch to the specified branch name."""
        if branch_name not in self.list_branches():
            setattr(self, "branch_name", None)
            raise exceptions.BranchNotFoundError(
                f"Branch '{branch_name}' does not exist. Please provide a valid branch "
                f"name."
            )
        setattr(self, "branch_name", branch_name)
        return self


    def current_branch(self) -> None:
        """Branch method to set the target branch to the current branch."""
        setattr(self, "branch_name", self.current_branch_name())
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
            self.current_branch_name(),
            self.commit_messages_path(),
            self.config_path(),
            self.document_path(),
            self.current_branch().history_path(),
            self.current_branch().byte_hashes_path()
        ]

        for i in dirs:
            if not i.is_dir():
                raise exceptions.InvalidMetadataError(
                    f"Required directory '{i}' not found. Please run 'sccs init "
                    f"<file_path>' to initialize SCCS for this file."
                )
            
        for i in files:
            if not i.is_file():
                raise exceptions.InvalidMetadataError(
                    f"Required file '{i}' not found. Please run 'sccs init "
                    f"<file_path>' to initialize SCCS for this file."
                )

        setattr(self, "branch_name", None)
            

    def check_for_uncommitted_changes(self, exit: bool = True) -> None | bool:
        """
        Check for uncommitted changes by hashing the current document bytes and comparing
        that to the latest commit bytes hash from the SCCS metadata.

        'cmd' is the command being run. It is used in the exception message.

        If exit is true, raise an UncommittedChangesError if uncommitted changes were found,
        if not return None.

        If 'exit' is false and uncommitted changes were found, return True, if not return
        False.

        'exit' defaults to True.
        """

        latest_commit = self.current_branch().get_latest_commit()

        
        latest_bytes_hash = self.current_branch().byte_hashes_data()[latest_commit]

        has_uncommitted_changes = latest_bytes_hash != self.convert_docx_to_binary_hash()

        if exit:
            if has_uncommitted_changes:
                raise exceptions.UncommittedChangesError(
                    f"Uncommitted changes were found. Please commit before continuing")

            setattr(self, "branch_name", None)
            return None

        setattr(self, "branch_name", None)
        return has_uncommitted_changes
        

    def branch_exists(self, branch_name: str) -> bool:
        """Return true if 'branch_name' exists in the repository, false if not."""
        exists = branch_name in self.list_branches()
        setattr(self, "branch_name", None)
        return exists


    def is_current_branch(self, branch_name: str) -> bool:
        """Return true if 'branch_name' is the current branch, false if not."""
        is_current = branch_name == self.current_branch_name()
        setattr(self, "branch_name", None)
        return is_current

# Convert Docuement


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

        setattr(self, "branch_name", None)
        return html_data
        

    def convert_docx_to_binary_hash(self) -> bytes:
        """
        Create and return a SHA-256 hash of the current DOCX file bytes, reading a 64KB
        chunk at a time.
        """
        try:
            with open(self.document_path(), "rb") as f:
                hasher = hashlib.sha256()
                for i in iter(lambda: f.read(65536), b""):
                    hasher.update(i)
                hashed_file = hasher.hexdigest()
        except Exception as e:
            raise exceptions.DocumentHashingError from e

        setattr(self, "branch_name", None)
        return hashed_file
    

# Commit uncommitted changes


    def commit_changes(self, commit_msg: str) -> str:
        """
        Commit uncommitted changes to the current branch using 'commit_msg' as the
        commit_message.
        """

        # region Commit Helpers


        def generate_commit_hash(self, commit_message: str) -> str:
            """Generate a SHA-256 hash for the commit."""

            return hashlib.sha256(
                f"{PROGRAM_START_TIME}/{commit_message}/{self.config_data('name')}/"
                f"{self.config_data('email')}/{self.current_branch().latest_commit()}".encode()
            ).hexdigest()


        def copy_docx_to_objects(self) -> None:
            """Copy the current document to the objects directory renamed to 'sha_hash'."""
            
            shutil.copy2(
                self.document_path(), 
                self.docx_objects_path() / f"{generate_commit_hash(PROGRAM_START_TIME)}.docx",
            )


        def write_docx_html(self) -> None:
            """
            Write the document as HTML to the objects directory, naming the file 'sha_hash'.
            """

            with open(
                self.html_objects_path() / f"{generate_commit_hash(PROGRAM_START_TIME)}.html",
                "w",
                encoding="utf-8",
                newline="\n",
            ) as f:
                f.write(utils.default_html_styles + self.convert_docx_to_html())


        def write_view_html(self) -> None:
            """
            Write the document HTML used for viewing, which is centered unlike the normal
            document HTML. Name the HTML file 'sha_hash'.
            """

            with open(
                self.view_html_objects_path() / f"{generate_commit_hash(PROGRAM_START_TIME)}.html",
                "w",
                encoding="utf-8",
                newline="\n",
            ) as f:
                f.write(utils.wrap_html(self.document_as_html()))


        def update_commit_binary_hash_history(self) -> dict[str, dict]:
            """Update the commit bytes hash history."""

            if not self.current_branch().byte_hashes_path().is_file():
                raise FileNotFoundError(
                    "Commit file hash not found. Please run 'sccs init <file_path>' to "
                    f"initialize SCCS for this file."
                )

            try:
                with open(self.current_branch().byte_hashes_path(), "r", encoding="utf-8", newline="\n") as f:
                    commit_file_hash = json.load(f)

            except Exception as e:
                raise exceptions.FileOpenError from e

            commit_file_hash[f"{generate_commit_hash(PROGRAM_START_TIME)}"] = self.convert_docx_to_binary_hash()

            return {self.current_branch().byte_hashes_path(): commit_file_hash}


        def update_commit_messages(self, commit_message) -> dict[str, dict]:
            """Update commit messages history."""

            # Check if commit messages file exists

            if not self.commit_messages_path().is_file():
                raise FileNotFoundError(
                    "Commit messages file not found. Please run 'sccs init <file_path>' to "
                    "initialize SCCS for this file."
                )

            with open(
                self.commit_messages_path(), "r", encoding="utf-8", newline="\n"
            ) as f:
                try:
                    messages = json.load(f)
                except Exception as e:
                    raise exceptions.FileOpenError from e

            messages[f"{generate_commit_hash(PROGRAM_START_TIME)}"] = f"{commit_message}"

            return {self.commit_messages_path(): messages}


        def update_commit_log_history(
            self, commit_message
        ) -> dict[str, dict]:
            """Update the commit log history."""

            # Check if history file exists
            if not self.current_branch().history_path().is_file():
                raise FileNotFoundError(
                    "History file not found. Please run 'sccs init <file_path>' to initialize "
                    "SCCS for this file."
                )

            history = self.current_branch().history_data()
            sha_hash = generate_commit_hash(PROGRAM_START_TIME)

            # Update history
            history["history"]["latest_commit"] = f"{sha_hash}"
            history["history"]["latest_commit_number"] = (
                history["history"].get("latest_commit_number", 0) + 1
            )

            latest_commit_number = history["history"]["latest_commit_number"]

            history["history"]["commit_order"][str(latest_commit_number)] = f"{sha_hash}"

            history["log"][f"{sha_hash}"] = {
                "timestamp": PROGRAM_START_TIME,
                "author": f"{self.config_data('name')} <{self.config_data('email')}>",
                "message": commit_message,
            }
            return {self.current_branch().history_path(): history}


        def update_changed_branches() -> dict[Path, dict] | None:
            """Update the list of branches with unpushed changes."""


            updated_branch = [self.current_branch_name()]            
            branch_data = self.current_branch_data()

            if "updated_branches" in branch_data and isinstance(
                branch_data["updated_branches"], list
            ):
                branch_data["updated_branches"] = list(
                    set(branch_data["updated_branches"] + updated_branch)
                )
            else:
                branch_data["updated_branches"] = updated_branch

            current_branch_name = self.current_branch_name()

            return {current_branch_name: branch_data}


        def combine_update_dicts(commit_message) -> dict[Path, dict]:
            """
            Combine multiple update dictionaries into a single dictionary for atomically
            updating document history metadata.
            """

            dicts = [
                update_commit_log_history(commit_message),
                update_commit_binary_hash_history(),
                update_commit_messages(commit_message),
                update_changed_branches()
            ]

            update_dict = {}
            for i in dicts:
                update_dict.update(i)
            return update_dict


        def atomically_update_history(update_dict: dict[Path, dict]) -> None:
            """
            For each pair in the dictionary, the key is a Path object and the value is a JSON
            dictionary. Write the JSON to temporary files, then rename the temporary files to
            atomically write.

            Open the key and write the value for each pair in the dictionary.
            """

            for i in update_dict.items():
                key, value = i
                try:
                    with open(
                        key.with_suffix(".tmp"), "w", encoding="utf-8", newline="\n"
                    ) as f:
                        json.dump(value, f)
                except Exception as e:
                    raise exceptions.TemporaryFileError from e

            for i in update_dict.items():
                key, value = i
                try:
                    key.with_suffix(".tmp").replace(key)
                except Exception as e:
                    raise exceptions.TemporaryFileError from e

        # endregion

        sha_hash = generate_commit_hash(commit_msg)

        copy_docx_to_objects()

        write_docx_html()

        write_view_html()

        atomically_update_history(combine_update_dicts(commit_msg))

        return sha_hash
 