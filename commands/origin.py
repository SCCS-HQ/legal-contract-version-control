import exceptions
import utils
from pathlib import Path
import json
import sys


def get_entered_origin() -> str | None:
    """Retrieve the origin entered by the user."""
    
    if len(sys.argv) > 2:
        entered_url = sys.argv[2]
        if not entered_url.startswith("http://") and not entered_url.startswith("https://"):
            entered_url = "http://" + entered_url
        
        strs = ["/clone", "/clone/", "/publish", "/publish/"]

        for str in strs:
            if entered_url.endswith(str):
                entered_url = entered_url[:-len(str)]

        return entered_url
    else:
        return None



def write_origin_to_config(remote: str = get_entered_origin()) -> None:
    """Write the origin to the config file."""

    with open(Path(utils.working_directory_path / ".sccs" / "config" / "config.json"), "r+", encoding="utf-8", newline="\n") as f:
        config = json.load(f)
        config["api_url"] = remote
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()


def main() -> None:
    """Run functions for the <sccs clone> command."""

    write_origin_to_config()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
else:
    raise exceptions.FileImportedAsModuleError(
        "This file cannot be run as a module. Please run it as a script."
    )
