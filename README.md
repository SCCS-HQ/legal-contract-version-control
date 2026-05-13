# 🎯 Simple Contracts Communication System, or SCCS

A lightweight distributed version control system designed to help legal professionals easily view and understand different versions of .docx files currently. ( .pdf files planned)

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

- While there are many different version control systems, many struggle to track diffs in .docx and .pdf files because they are binary. SCCS solves this by converting .pdf and .docx files to .txt and keeping a .txt version after each commit.
  
- SCCS is for legal professionals searching for a better way to track and view file changes of contracts.
  
- Currently, most version control for contracts is just multiple versions of mostly identical files, emailed back and forth between people. Storing .txt files and keeping less XML metadata as files can share it. It also cleanly shows diff between version of a file, instead of between different files

## ✨ Features

CLI interface to:

- Initialize new .docx 

- Commit changes to an existing docx

- Compare the current version of the docx to an earlier commit as HTML split diff

- Open previous commits

- View a history log of all commits

- Check the status (i.e. have there been changes)

- Get help/tips (i.e. lists all commands and their function)

- Create and switch to different branches

## 🚧 Features Coming Soon (WIP)

- Host repository online like Git

- Word diff engine to track changes by clause

## 📦 Installation

```bash
# Clone the Git Repository
git clone https://github.com/slveer/legal-contract-version-control.git

# Install all required dependencies
pip install -r requirements.txt
```

## Setup
MacOS / Linux

```bash
# Copy all repo CLI files to /usr/local/bin/
sudo cp commit.py diff.py help.py init.py default_css_styles.py log.py open.py status.py sccs

# Make SCCS file executable
sudo chmod +x /usr/local/bin/sccs
```

Windows

TBA

## 🤝 Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for info on how to get started contributing! It is greatly appreciated 😁 !

## 📃 License
SCCS uses the GPLv3, which you can find in [LICENSE](LICENSE)
