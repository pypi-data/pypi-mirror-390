from dataclasses import dataclass
import sys
import os


@dataclass
class PythonInfo:
    version: str
    executable_path: str
    script_path: str


def whoruv():
    return PythonInfo(
        version=sys.version,
        executable_path=sys.executable,
        script_path=os.path.abspath(__file__),
    )


def format_python_info(info: PythonInfo) -> str:
    return f"""Python Version: {info.version}
Executable Path: {info.executable_path}
Script Path: {info.script_path}
"""
