# File Integrity Monitoring (FIM) Tool – Python CLI
File Integrity Monitoring application. A python based FIM tool that tracks modified files from base folder

## Overview
A lightweight, cross-platform File Integrity Monitoring (FIM) tool developed in Python to provide reliable file integrity verification using cryptographic hash functions. Designed with portability and simplicity in mind, the tool operates entirely from the command line, requiring no installation or graphical interface.

* Portable. Run anytime, anywhere (as long as python is installed on a system)
* Generate and verify checksums (SHA1, SHA512, and SHA256)
* Compare current file hash with known hash
* Full CLI for simplicity. No UI needed

# 📦 Installation

```bash
git clone https://github.com/yourusername/file-integrity-checker.git
cd file-integrity-checker
python3 FIM.py "./root"
Now the File Integrity Checker will scan...
```
