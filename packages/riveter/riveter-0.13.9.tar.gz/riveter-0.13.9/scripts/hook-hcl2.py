#!/usr/bin/env python3
"""PyInstaller hook for hcl2 module.

This hook ensures that the HCL grammar file (hcl2.lark) is properly
included in the PyInstaller bundle and can be found at runtime.
"""

from PyInstaller.utils.hooks import collect_data_files

# Collect all data files from hcl2 package (includes hcl2.lark)
datas = collect_data_files("hcl2")

# Also specify hidden imports if needed
hiddenimports = [
    "hcl2.parser",
    "hcl2.api",
    "lark",
    "lark.parsers",
    "lark.lexer",
    "lark.grammar",
]
