# jps-test-artifact-python-utils

![Test](https://github.com/jai-python3/jps-test-artifact-python-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-test-artifact-python-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-test-artifact-python-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-test-artifact-python-utils)


Utilities for creating, verifying, and managing **test artifact directories** used to support functional testing of command-line executables.
Includes CLI tools for setting up test directories, generating MD5 manifests, and validating test data integrity.

---

## 🧩 Installation

```bash
pip install jps-test-artifact-python-utils
```

or install in editable mode for local development:

```bash
git clone git@github.com:jai-python3/jps-test-artifact-python-utils.git  
cd jps-test-artifact-python-utils  
pip install -e .
```

---

## 🧩 setup-test-artifacts

Sets up a new test artifact instance directory by copying representative input, output, and script files into a new workspace.

### Usage

```bash
setup-test-artifacts --indir <test-case-dir> [--script-dir <scripts-dir>]
```

### Example

```bash
setup-test-artifacts --indir synthentic-genomics-pipeline/v1.2.0/comp_analysis/test-case-001/
```

This generates a fully configured test workspace with expected structure and a runnable shell script.

---

## 🧩 create-md5-manifest

Generates an `md5_manifest.txt` file listing all files under a given directory with their MD5 checksums, sizes, and timestamps.

### Usage

```bash
create-md5-manifest --test-case-dir <path> --manifest-file <path>
```

### Example Output

```text
## method-created: /scripts/create_md5_manifest.py
## date-created: 2025-10-28 13:22:01
## created-by: jsundaram
## Columns:
## 1: relative file path
## 2: md5sum
## 3: number of bytes
## 4: date/time md5sum was derived

inputs/sample_input.vcf  3d883acf1a3db79c3390b8a96570a2ec  2145  2025-10-28-13:22:03
outputs/expected_output.tsv  53754d366f5676075a00e4c979f85cae  907  2025-10-28-13:22:04
```

---

## 🧩 verify-md5-manifest

Compares the current MD5 checksums of files in a test artifact directory with a saved manifest, reporting any mismatches or missing files.

### Usage

```bash
verify-md5-manifest --test-case-dir <path> --manifest-file <path>
```

### Example Output

```bash
✔ inputs/sample_input.vcf
✔ outputs/expected_output.tsv
✘ outputs/altered_output.tsv

2 of 3 files passed
Files with mismatched MD5 sums:
File: outputs/altered_output.tsv
Current MD5: 25a89f...
Previous MD5: 53754d...
```

---

## 🗂 Example Test Artifact Directory Layout

```text
synthentic-genomics-pipeline/v1.2.0/comp_analysis/test-case-001/
├── inputs/
│   ├── sample_input.bam
│   ├── sample_input.vcf
│   └── genes.fasta
├── outputs/
│   └── expected_output.tsv
└── scripts/
    ├── requirements.txt
    └── run_test_case.sh.tmpl
```

---

## 🧾 Logging

Logs follow this format:

```text
LOG_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"
```

- Only **WARNING and above** are printed to STDERR.  
- **INFO, WARNING, ERROR, and FATAL** are all written to the log file.

---

## 🧪 Development and Testing

Install dependencies for linting, formatting, and testing:

```bash
pip install -e '.[dev]'
```

Run all lint and test checks:

```bash
make lint  
make test
```

---

## 🧾 License

MIT License  
© 2025 Jaideep Sundaram
