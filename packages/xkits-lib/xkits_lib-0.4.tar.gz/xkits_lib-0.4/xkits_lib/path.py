# coding=utf-8

import os
from typing import List

from xkits_lib.utils import singleton


@singleton
class Workspace:
    """Change working directory"""

    def __init__(self):
        self.__stack: List[str] = []

    @property
    def cwd(self) -> str:
        """Get current working directory."""
        return os.getcwd()

    @cwd.setter
    def cwd(self, path: str):
        """Set current working directory."""
        self.pushd(path)

    def pushd(self, path: str):
        """Add current working directory to stack and change working directory."""  # noqa:E501
        assert isinstance(path, str), f"type '{type(path)}' is not str"
        assert os.path.isdir(path), f"path '{path}' is not directory"
        self.__stack.append(self.cwd)
        os.chdir(path)

    def popd(self):
        """Remove directory from stack and change working directory."""
        assert len(self.__stack) > 0
        os.chdir(self.__stack.pop())
