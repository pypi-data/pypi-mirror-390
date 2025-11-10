# tds-flatpath

Reversible, collision-proof filename flattening for storing hierarchical paths in **flat namespaces** (object stores, zip members, cache keys, build artifacts, etc.) — while keeping names **human-readable**.

Unlike hashing or escape-heavy encodings, `tds-flatpath` preserves meaningful stems and grows only as needed to resolve actual ambiguity (underscore density + depth). No side tables. Fully deterministic. Exactly reversible.

**Use cases include:**
- Storing directory trees in S3 / MinIO / Azure blob stores
- Packaging project resources inside zip/tar layers
- Cache key derivation where readability matters
- Stable artifact naming across environments and OSes

**Guarantees:** (see [tds-flatpath_Specification](https://github.com/XRReady/tds-flatpath/blob/main/tds-flatpath_Specification.md))
- No collisions: mapping is **injective**
- Fully reversible: decode returns the original path array
- Human-visible stems stay readable
- Extension preserved exactly
- Scales only with actual underscore usage and directory depth


> Built by [Texas Data Safe (tds)](https://x.com/TexasDataSafe). Designed for packaging file trees into flat stores (object stores, zip members, temp dirs, cache keys) without losing reversibility or readability.

## Project structure

```

tds-flatpath/
├── src/
│   └── tds_flatpath/
│       ├── **init**.py         # Exports TdsFlatNameCodecV1
│       └── codec.py            # Core reversible flattening logic
├── tests/
│   ├── benchmark.py            # compare performance against SHA256
│   └── test_codec.py           # Unit tests for codec behavior
├── tds-flatpath_Specification  # Language angostic specification
├── pyproject.toml              # Build & packaging configuration
├── README.md                   # Project documentation
├── LICENSE                     # MIT license
└── CITATION.cff                # Citation metadata

```

## Why this over hashing or length-prefixed joins?

- **Human-readable** stems (`src_module_mhello.py`) instead of opaque hashes.
- **Deterministic and reversible**: an underscore-run “postfix” encodes only the ambiguity you need to resolve (underscore counts + directory depth).
- **Shorter than hashes** for typical paths; scales with actual collisions, not worst-case characters.
- **Provably collision-free** (injective mapping), unlike hashes which provide *statistical* collision resistance. Fine in practice, but is the principle of the matter, right? ;)

## Install

```bash
pip install tds-flatpath
````

Python 3.8+ recommended.

## Quick start

```python
from tds_flatpath import TdsFlatNameCodecV1

tdsFNC = TdsFlatNameCodecV1()

print(tdsFNC.flat_name(["README.md"]))
# -> README.md

print(tdsFNC.flat_name(["src", "README.md"]))
# -> src_README.md_-

print(tdsFNC.flat_name(["src", "module", "mhello.py"]))
# -> src_module_mhello.py_--

print(tdsFNC.flat_name(["src", "module", "__init__.py"]))
# -> src_module___init__.py_--n2n2

print(tdsFNC.flat_name(["src", "a_b", "c_d.txt"]))
# -> src_a_b_c_d.txt_-n1-n1

print(tdsFNC.unflatten_to_path("src_a_b_c_d.txt_-n1-n1"))
# -> ['src', 'a_b', 'c_d.txt']

print(tdsFNC.unflatten_to_path(tdsFNC.flat_name(["src","a_b","c_d","stubcode.py"])))
# -> ['src', 'a_b', 'c_d', 'stubcode.py']
```

## Specification (V1)

The encoding format used by `tds-flatpath` is precisely defined in a stable,
versioned specification document:

[**tds-flatpath Specification (V1)** ](https://github.com/XRReady/tds-flatpath/blob/main/tds-flatpath_Specification.md)

This specification guarantees:

* Deterministic, collision-proof mapping
* Full reversibility (no metadata side-tables required)
* Human-readable flattened names
* Growth proportional only to actual underscore ambiguity and depth

The current implementation `TdsFlatNameCodecV1` conforms to **Format Version V1**
as defined in that document. Any future encoding changes will appear under
`V2`, `V3`, etc.


## How it works

* We join segments with `_` **only in the base** (e.g., `src_a_b_c.txt`).
* A compact **postfix** after a final underscore captures:
  * counts of consecutive `_` **inside** each original segment (`n<HEX>` tokens),
  * and `-` markers for **directory boundaries**.
* With that, decoding is deterministic and collision-proof.

Example:

```
['src', 'a_b', 'c___d.txt']
flatten -> "src_a_b_c___d.txt_-n1-n3"
```

## Benchmark Results

You can run the benchmark locally:

```bash
cd tests
python benchmark.py
```

No installation is required if the repository is cloned directly.
The benchmark also works when the package is installed in an environment.

### System Information

```
Platform: Windows 11 (10.0.26100)
Machine: AMD64
Processor: AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD
CPU Cores: 12
Python: 3.13.2
CPU Frequency: 3.90 GHz (max 3.90 GHz)
RAM: 133.05 GB
```

### Length Benchmark

| Sample | Path Example (truncated)          | tds-flatpath Len | SHA256 Len | Length-Prefixed Len |
| ------ | --------------------------------- | ---------------- | ---------- | ------------------- |
| 1      | README.md                         | 9                | 67         | 11                  |
| 2      | src/README.md                     | 15               | 67         | 17                  |
| 3      | src/module/mhello.py              | 23               | 67         | 26                  |
| 4      | src/a_b/c_d.txt                   | 22               | 68         | 21                  |
| 5      | src/a/b/c_d.txt                   | 21               | 68         | 23                  |
| 6      | src/a__b_a_b/c___d.txt            | 33               | 68         | 28                  |
| 7      | very/deep/path/with/many/level... | 47               | 68         | 54                  |
| 8      | file_with_many___underscores__... | 45               | 68         | 39                  |
| 9      | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa... | 104              | 68         | 108                 |
| 10     | dir1/dir2/dir3/dir4/dir5/file.... | 38               | 67         | 44                  |
| 11     | **********a**********_________... | 41               | 68         | 38                  |

**Averages**

* tds-flatpath: 36.2
* SHA256: 67.6
* Length-Prefixed: 37.2

### Time Benchmark (10,000 Random Paths)

| Method                         | Time (seconds) |
| ------------------------------ | -------------- |
| tds-flatpath (with validation) | 0.4021         |
| tds-flatpath (no validation)   | 0.3995         |
| SHA256                         | 0.3587         |
| Length-Prefixed                | 0.3548         |


## API

```python
class TdsFlatNameCodecV1:
    @classmethod
    def flat_name(cls, path_array: list[str]) -> str: ...
    @classmethod
    def unflatten_to_path(cls, flattened_filename: str) -> list[str]: ...

    # Utilities (mainly for advanced/debug use):
    @classmethod
    def split_base_ext_postfix(cls, filename: str) -> tuple[str, str, str]: ...
    @classmethod
    def split_base_postfix_ext(cls, filename: str) -> tuple[str, str, str]: ...
    @classmethod
    def postfix_to_counts(cls, postfix: str) -> list[int]: ...
```

**Constraints**

* `path_array` must be non-empty, each element a plain string segment without OS separators.
* Extensions are preserved; files like `.gitignore` are handled.

## Edge cases covered

* Files with no underscores need no postfix when there’s no directory context.
* Pure extension names (e.g., `.env`) keep behavior intuitive.
* Deep paths with heavy underscore usage remain reversible.

## Versioning & compatibility

* Current version: **0.1.0**
* Postfix format: `V1` (stable). Future formats will bump the class/version.

## License

MIT — feel free to use in open source or commercial projects.
**Please retain credit to Texas Data Safe (tds) / Dale Spencer.**

## Contributing

Issues and PRs welcome. Please include:

* a failing test case for bugs,
* before/after examples for behavior changes.

## Cite this project

If this helps your work, please cite (see `CITATION.cff`):

```
Spencer, D. (2025). tds-flatpath (Version 0.1.0). Texas Data Safe.
```
