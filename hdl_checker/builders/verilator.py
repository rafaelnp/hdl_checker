# This file is part of HDL Checker.
#
# Copyright (c) 2015 - 2019 suoto (Andre Souto)
#
# HDL Checker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HDL Checker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDL Checker.  If not, see <http://www.gnu.org/licenses/>.
"Verilator builder implementation"

import os
import os.path as p
import re
from glob import glob
from typing import Any, Iterable, List, Optional

from .base_builder import BaseBuilder

from hdl_checker.diagnostics import BuilderDiag, DiagType
from hdl_checker.parsers.elements.identifier import Identifier
from hdl_checker.path import Path
from hdl_checker.types import BuildFlags, BuildFlagScope, FileType
from hdl_checker.utils import runShellCommand


class Verilator(BaseBuilder):
    """
    Builder implementation of the Verilator compiler
    """

    # Implementation of abstract class properties
    builder_name = "verilator"
    file_types = {FileType.verilog, FileType.systemverilog}

    # Default build flags
    default_flags = {
        BuildFlagScope.all: {
            FileType.verilog: ("-Wall"),
            FileType.systemverilog: ("-Wall", "-sv"),
        },
    }

    def __init__(self, *args, **kwargs):
        self._version = ""
        super(Verilator, self).__init__(*args, **kwargs)

    def _shouldIgnoreLine(self, line):
        pass

    def _makeRecords(self, line):
        pass

    def _buildSource(self, path, library, flags=None):
        pass

    def _createLibrary(self, library):
        pass

    def _checkEnvironment(self):
        stdout = runShellCommand("verilator --version", shell=True)
        self._version = re.findall(r"(?<=Verilator)\s+([^\s]+)\s+", stdout[0])[0]
        self._logger.info(
            "Verilator version string: '%s'. " "Version number is '%s'",
            stdout[:-1],
            self._version,
        )

    @staticmethod
    def isAvailable():
        try:
            runShellCommand("verilator --version", shell=True)
            return True
        except OSError:
            return False
