import hashlib
import json
from pathlib import Path

import mammoth
import exceptions


class RepositoryLayout:
    def __init__(self, root: Path):
        self.root = root

        branches = [i for i in (root / ".sccs" / "branches").iterdir() if i.is_dir()]

        for file in branches.iterdir():
            def make_method(f):
                def method(self):
                    setattr(self, f.stem, f)
                    setattr(self, "target_branch", f.stem)

                    return self
                return method
            
            method_name = f"{file.stem}_branch"
            setattr(self.__class__, method_name, make_method(file))

# Return Files or Folder Paths


    def document_path(self) -> Path:
        """Return the path to the current document."""
        path = self.root / f"{self.root.name}.docx"
        setattr(self, "target_branch", None)
        return path
    

    def sccs_path(self) -> Path:
        """Return the path to the '.sccs' folder."""
        path = self.root / ".sccs"
        setattr(self, "target_branch", None)
        return path
    

    def branches_path(self) -> Path:
        """Return the path to the 'branches' folder."""
        path = self.sccs_path() / "branches"
        setattr(self, "target_branch", None)
        return path
    

    def commit_messages_path(self) -> Path:
        """Return the path to the 'commit_messages.json' file."""
        path = self.sccs_path() / "commit_messages" / "commit_messages.json"
        setattr(self, "target_branch", None)
        return path
    

    def config_path(self) -> Path:
        """Return the path to the 'config.json' file."""
        path = self.sccs_path() / "config" / "config.json"
        setattr(self, "target_branch", None)
        return path
    

    def current_branch_path(self) -> Path:
        """Return the path to the 'current_branch.json' file."""
        path = self.sccs_path() / "current_branch" / "current_branch.json"
        setattr(self, "target_branch", None)
        return path
    

    def objects_path(self) -> Path:
        """Return the path to the 'objects' folder."""
        path = self.sccs_path() / "objects"
        setattr(self, "target_branch", None)
        return path
    

    def docx_objects_path(self) -> Path:
        """Return the path to the 'docx' objects folder."""
        path = self.objects_path() / "docx"
        setattr(self, "target_branch", None)
        return path
    

    def view_html_objects_path(self) -> Path:
        """Return the path to the 'view_html' objects folder."""
        path = self.objects_path() / "view_html"
        setattr(self, "target_branch", None)
        return path
    

    def html_objects_path(self) -> Path:
        """Return the path to the 'html' objects folder."""
        path = self.objects_path() / "html"
        setattr(self, "target_branch", None)
        return path
    

    def history_path(self) -> Path:
        """
        Return the path to the 'history.json' file for the current branch. Chaining this
        method with a branch method is required.
        """
        
        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling history_path(). For example,"
                "'repo_layout.main_branch().history_path()'."
            )

        path = self.branches_path() / self.target_branch / "history" / "history.json"
        setattr(self, "target_branch", None)
        return path


    def byte_hashes_path(self) -> Path:
        """
        Return the path to the 'commit_files_hash.json' file for the current branch. 
        Chaining this method with a branch method is required.
        """
        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling byte_hashes_path(). For example,"
                "'repo_layout.main_branch().byte_hashes_path()'."
            )

        path = self.branches_path() / self.target_branch / "commit_files_hash" / "commit_files_hash.json"
        setattr(self, "target_branch", None)
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

        setattr(self, "target_branch", None)
        return matching_files[0]


# Return Data from Files


    def current_branch_data(self, key: str | None = None) -> dict | str | None:
        """
        Return the current branch data from the 'current_branch.json' file. If 'key' is
        provided, return the value of that key from the current branch data.
        """

        with open(self.current_branch_path(), "r", encoding="utf-8", newline="\n") as f:
            branch_data = json.load(f)
        if key is None:
            setattr(self, "target_branch", None)
            return branch_data
        setattr(self, "target_branch", None)
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

        setattr(self, "target_branch", None)
        return config_data.get(key)
    

    def history_data(self) -> dict:
        """
        Return the history data from the 'history.json' file for the current branch.
        Chaining this method with a branch method is required.
        """

        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling history_data(). For example,"
                "'repo_layout.main_branch().history_data()'."
            )

        with open(
            self.branches_path() /
            self.target_branch /
            "history" /
            "history.json", "r", encoding="utf-8", newline="\n"
        ) as f:
            history_data = json.load(f)

        setattr(self, "target_branch", None)
        return history_data
    

    def byte_hashes_data(self) -> dict:
        """
        Return the byte hashes data from the 'commit_files_hash.json' file for the 
        current branch. Chaining this method with a branch method is required.
        """
        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please chain this method call with a branch "
                "method before calling byte_hashes_data(). For example,"
                "'repo_layout.main_branch().byte_hashes_data()'."
            )

        with open(
            self.branches_path() /
            self.target_branch /
            "commit_files_hash" /
            "commit_files_hash.json", "r", encoding="utf-8", newline="\n"
        ) as f:
            byte_hashes_data = json.load(f)

        setattr(self, "target_branch", None)
        return byte_hashes_data

# Return Miscellaneous Data


    def list_branches(self) -> list[str]:
        setattr(self, "target_branch", None)
        return [self.branches]


    def current_branch_name(self) -> str:
        with open(self.current_branch_path(), "r", encoding="utf-8", newline="\n") as f:
            current_branch_data = json.load(f)
        setattr(self, "target_branch", None)
        return current_branch_data["current_branch"]
    
    
    def latest_commit(self) -> str | None:
        """
        Retrieve the latest commit hash from the commit history of the current branch.
        Chaining this method with a branch method is required.
        """
        if self.target_branch is None:
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
        
        setattr(self, "target_branch", None)
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

        setattr(self, "target_branch", None)



# Set edit branch status


    def branch(self, branch_name: str) -> None:
        """Branch method to set the target branch to the specified branch name."""
        if branch_name not in self.list_branches():
            setattr(self, "target_branch", None)
            raise exceptions.BranchNotFoundError(
                f"Branch '{branch_name}' does not exist. Please provide a valid branch "
                f"name."
            )
        setattr(self, "target_branch", branch_name)
        return self


    def current_branch(self) -> None:
        """Branch method to set the target branch to the current branch."""
        setattr(self, "target_branch", self.current_branch_name())
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
                    f"Required directory '{i}' not found. Please run 'sccs init "
                    f"<file_path>' to initialize SCCS for this file."
                )
            
        for i in files:
            if not i.is_file():
                raise exceptions.InvalidMetadataError(
                    f"Required file '{i}' not found. Please run 'sccs init "
                    f"<file_path>' to initialize SCCS for this file."
                )

        setattr(self, "target_branch", None)
            

    def check_for_uncommitted_changes(self, cmd: str, exit: bool = True) -> None | bool:
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

            setattr(self, "target_branch", None)
            return None

        setattr(self, "target_branch", None)
        return has_uncommitted_changes
        

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

        setattr(self, "target_branch", None)
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

        setattr(self, "target_branch", None)
        return hashed_file