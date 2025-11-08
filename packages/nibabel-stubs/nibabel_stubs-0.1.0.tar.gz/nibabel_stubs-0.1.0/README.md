# nibabel-stubs

Type stubs for [nibabel](https://nipy.org/nibabel/), a Python package for reading and writing neuroimaging file formats.

## Installation

```bash
pip install nibabel-stubs
```

## Usage

Once installed, type checkers like mypy, pyright, and IDEs like PyCharm and VS Code will automatically use these type stubs when you use nibabel in your code.

Example:

```python
import nibabel as nib

# Type checkers will now understand nibabel's API
img = nib.load("example.nii.gz")
data = img.get_fdata()
affine = img.affine
header = img.header
```

## What's Included

This package provides type hints for:

- `Nifti1Image` and `Nifti1Header` classes
- `load()` and `save()` functions
- `affines` module utilities
- `orientations` module utilities
- Common nibabel operations with proper numpy array typing

## Requirements

- Python >= 3.7
- numpy (for numpy.typing support)

## Development

To contribute or modify these stubs:

1. Clone the repository
2. Edit `nibabel-stubs/__init__.pyi`
3. Test with your type checker:
   ```bash
   mypy your_test_file.py
   ```

## License

See [LICENSE.md](LICENSE.md) for details.

## Compatibility

These stubs are designed to work with nibabel's public API. If you find any issues or missing definitions, please open an issue or submit a pull request.

