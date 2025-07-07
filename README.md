# File Integrity Monitoring (FIM) Tool – Python CLI
## Overview

A lightweight, cross-platform File Integrity Monitoring (FIM) tool developed in Python to provide reliable file integrity verification using cryptographic hash functions. Designed with portability and simplicity in mind, the tool operates entirely from the command line, requiring no installation or graphical interface.

## Key features
* Portability: Runs on any system with Python installed. No dependencies or installation required.
* Multi-Hash Support: Supports SHA1, SHA256, and SHA512 algorithms for checksum generation and verification.
* Integrity Verification: Compares current file hashes against known (baseline) values to detect tampering or corruption.
* Console-Based: Built as a command-line interface for ease of automation, scripting, and minimal resource usage.

## Use Cases
* Verifying file integrity after transfer, backup, or deployment
* Detecting unauthorized changes to sensitive files or configuration assets
* Lightweight alternative to complex FIM or endpoint protection platforms in constrained environments

## Benefits
* Minimal footprint and high portability make the tool ideal for use in secure, low-resource, or isolated environments.
* Hash algorithm flexibility supports varying levels of security or compliance requirements.
* CLI design enables seamless integration into existing shell scripts, cron jobs, or DevOps workflows.

# Installation

```bash
git clone https://github.com/yujin-xin/File-integrity-monitoring
cd File-integrity-monitoring
python3 FIM.py "./root"
```
