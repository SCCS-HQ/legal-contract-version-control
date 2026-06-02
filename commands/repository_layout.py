from pathlib import Path

class RepositoryLayout:
    def __init__(self, root: Path):
        self.root = root

        branches = root / ".sccs" / "branches"

        for file in branches.iterdir():
            def make_method(f):
                def method(self):
                    setattr(self, f.stem, f)
                    setattr(self, "target_branch", f.stem)

                    return self
                return method
            
            method_name = f"{file.stem}_branch"
            setattr(self.__class__, method_name, make_method(file))

    def document(self) -> Path:
        return self.root / f"{self.root.name}.docx"
    
    def sccs(self) -> Path:
        return self.root / ".sccs"
    
    def branches(self) -> Path:
        return self.sccs() / "branches"
    
    def commit_messages(self) -> Path:
        return self.sccs() / "commit_messages" / "commit_messages.json"
    
    def config(self) -> Path:
        return self.sccs() / "config" / "config.json"
    
    def current_branch(self) -> Path:
        return self.sccs() / "current_branch" / "current_branch.json"
    
    def objects(self) -> Path:
        return self.sccs() / "objects"
    
    def docx_objects(self) -> Path:
        return self.objects() / "docx"
    
    def view_html_objects(self) -> Path:
        return self.objects() / "view_html"
    
    def html_objects(self) -> Path:
        return self.objects() / "html"
    
    def history(self) -> Path:
        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please call a branch method before calling " 
                "history()."
            )

        path = self.branches() / self.target_branch / "history" / "history.json"
        setattr(self, "target_branch", None)
        return path

    def byte_hashes(self) -> Path:
        if self.target_branch is None:
            raise ValueError(
                "Target branch not set. Please call a branch method before calling " 
                "byte_hashes()."
            )

        path = self.branches() / self.target_branch / "byte_hashes" / "byte_hashes.json"
        setattr(self, "target_branch", None)
        return path
        

    def list_branches(self) -> list[str]:
        return [i.stem for i in self.branches().iterdir() if i.is_dir()]