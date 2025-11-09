"""
This file is part of pyFFEDITC.

Copyright (C) 2025 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import subprocess


def compress(input_path: str, output_path: str, ffeditc_exe_path: str) -> bool:
    """
    Compresses a file using the ffeditc_unicode.exe utility.

    Args:
        input_path (str): Path to the uncompressed input file.
        output_path (str): Path where the compressed file will be saved.
        ffeditc_exe_path (str): Path to the TK.MSTS.Tokens DLL.

    Raises:
        EnvironmentError: If required runtime dependencies are missing.
        FileNotFoundError: If the DLL cannot be found.
        ImportError: If the DLL cannot be loaded.

    Returns:
        bool: True if compression succeeded, False otherwise.
    """
    directory = os.path.dirname(ffeditc_exe_path)
    executable = os.path.basename(ffeditc_exe_path)

    try:
        result = subprocess.run(
            [executable, input_path, "/c", "/o:" + output_path],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )

        print("Standard output:\n", result.stdout)
        print("Standard error:\n", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("Error output:\n", e.stderr)
        return False


def decompress(input_path: str, output_path: str, ffeditc_exe_path: str) -> bool:
    """
    Decompresses a file using the ffeditc_unicode.exe utility.

    Args:
        input_path (str): Path to the compressed input file.
        output_path (str): Path where the decompressed file will be saved.
        ffeditc_exe_path (str): Path to the TK.MSTS.Tokens DLL.

    Raises:
        EnvironmentError: If required runtime dependencies are missing.
        FileNotFoundError: If the DLL cannot be found.
        ImportError: If the DLL cannot be loaded.

    Returns:
        bool: True if decompression succeeded, False otherwise.
    """
    directory = os.path.dirname(ffeditc_exe_path)
    executable = os.path.basename(ffeditc_exe_path)

    try:
        result = subprocess.run(
            [executable, input_path, "/u", "/o:" + output_path],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )

        print("Standard output:\n", result.stdout)
        print("Standard error:\n", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("Error output:\n", e.stderr)
        return False

