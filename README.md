# 🎯 Simple Contracts Communication System, or SCCS

A lightweight CLI distributed version control system designed to help legal professionals easily view and understand different versions of .docx files.

## ⚠️ Please Read
- **Repositories or clones created with older SCCS versions cannot currently be migrated to newer SCCS versions; please re-clone the repository or re-initialize SCCS instead.**
- Build Status: Pre-Alpha
- License: GPLv3


---

## 📁 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Installation](#-installation)
- [Setup](#-setup)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](mailto:danielaphillion@gmail.com)

## 🧠 About

- While there are many different version control systems, many struggle to track diffs in .docx files because they are binary. SCCS solves this by converting .docx files to HTML using [Mammoth](https://github.com/mwilliamson/python-mammoth), and keeping a HTML version of each commit.
  
- SCCS is for legal professionals searching for a better way to track and view file changes of contracts.
  
- Currently, most version control for contracts is just multiple versions of mostly identical files, emailed back and forth between people. Storing a folder of history metadata, hidden from the user simplifies this process. It also cleanly shows diff between version of a file, as opposed to between different files.

## ✨ Features

CLI Commands:

```Python
sccs branch - Create a new branch, delete, or list branches.
sccs clone - Clone a hosted SCCS repository with a URL.
sccs commit - Commit changes to the repository.
sccs config - Configure a repository's data value (remote, name, email)
sccs diff - Show differences between the current document and a past commit.
sccs help - Print this help message.
sccs init - Initialize a new SCCS repository.
sccs log - Print a list of past commits for the current branch.
sccs open - Open a commit file and update the current document.
sccs publish - Publish a local repository to a hosting service.
sccs pull - Pull changes from a remote repository and merge them into the local repository.
sccs push - Push changes from the local repository to a remote repository.
sccs revert - Revert the current document to the specified commit.
sccs reset - Delete all uncommitted changes.
sccs switch - Switch between document branches.
sccs status - Check the status of the current document for uncommitted changes.
sccs merge - Merge the entered branch into the current branch.
```

## 📦 Installation

```bash
# Clone the Git Repository
git clone https://github.com/SCCS-HQ/legal-contract-version-control.git

# Install all required dependencies
pip install -r requirements.txt
```

## Setup
MacOS / Linux

```bash
# Copy all repo CLI files to /usr/local/bin/
sudo cp commands/* /usr/local/bin/

# Make SCCS file executable
sudo chmod +x /usr/local/bin/sccs
```

Windows

TBA

## 🤝 Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for info on how to get started contributing! It is greatly appreciated 😁 !

## 📃 License
SCCS uses the GPLv3, which you can find in [LICENSE](LICENSE)
