# USDM4_Excel

Library for import and export of USDM Version 3 via MS Excel. The package exports from USDM4 data.

# Build Package

Build steps for deployment to pypi.org

- Build with `python3 -m build --sdist --wheel`
- Upload to pypi.org using `twine upload dist/*`