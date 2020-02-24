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

    # Verilator specific class properties
    _stdout_message_scanner = re.compile(
        r"""^\%(?P<severity>((\w+\-\w+)|(\w+)))\:
        \s*(?P<filename>\w+\.(v|sv))\:
        (?P<line_number>\d+)\:\s*
        (?P<error_message>(.*\n.*\n.*)|(.*\n.*))""",
        flags=re.VERBOSE,
    ).finditer

    # Default build flags
    default_flags = {
        BuildFlagScope.single: {
            FileType.verilog: ("--lint-only -Wpedantic -Wall"),
            FileType.systemverilog: ("--lint-only -Wall -Wpedantic ", "-sv"),
        },
        BuildFlagScope.all: {
            FileType.verilog: ("--lint-only -Wpedantic -Wall"),
            FileType.systemverilog: ("--lint-only -Wall -Wpedantic ", "-sv"),
        },
    }

    def __init__(self, *args, **kwargs):
        """
        class constructor
        """
        self._version = ""
        super(Verilator, self).__init__(*args, **kwargs)

    def _shouldIgnoreLine(self, line):
        pass

    def _makeRecords(self, line):
        """
        gather the warning/error information to be shown to the  user
        """
        # type: (str) -> Iterable[BuilderDiag]
        for match in self._stdout_message_scanner(line):  # type: ignore
            info = match.groupdict()

            self._logger.debug("Parsed dict: %s", repr(info))

            filename = info.get("filename", None)
            line_number = info.get("line_number", None)

            if info.get("severity", None) in ("Warning", "Error"):
                severity = DiagType.WARNING
            else:
                severity = DiagType.ERROR

            yield BuilderDiag(
                builder_name=self.builder_name,
                text=info.get("error_message", None),
                filename=None if filename is None else Path(filename),
                severity=severity,
                line_number=None if line_number is None else int(line_number) - 1,
            )

    def _createLibrary(self, library):
        if p.exists(p.join(self._work_folder, library.name)):
            self._logger.debug("Path for library '%s' already exists", library)
            return
        self._mapLibrary(library)
        self._logger.debug("Added and mapped library '%s'", library)

    def _checkEnvironment(self):
        """
        check and print the builder version
        """
        stdout = runShellCommand("verilator --version", shell=True)
        self._version = re.findall(r"(?<=Verilator)\s+([^\s]+)\s+", stdout[0])[0]
        self._logger.info(
            "Verilator version string: '%s'. " "Version number is '%s'",
            stdout,
            self._version,
        )

    @staticmethod
    def isAvailable():
        """
        check if verilator is installed/present in the system $PATH
        """
        try:
            runShellCommand("verilator --version", shell=True)
            return True
        except OSError:
            return False

    def _buildSource(self, path, library, flags=None):
        # type: (Path, Identifier, Optional[BuildFlags]) -> List[str]
        """
        Runs Verilator with syntax check switch
        """
        filetype = FileType.fromPath(path)

        if filetype in (FileType.verilog, FileType.systemverilog):
            self._logger("detected valid file: '%s'", path)
            return self._buildVerilog(path, library, flags)

        self._logger.error("Unknown file type %s for path '%s'",
                           filetype, path)

        return ""

    def _buildVerilog(self, path, library, flags=None):
        # type: (Path, Identifier, Optional[BuildFlags]) -> Iterable[str]
        """
        Builds a Verilog/SystemVerilog file
        """
        cmd = [
            "verilator",
            "--cc",
            "-O0",
            p.join(self._work_folder, library.name),
        ]

        if FileType.fromPath(path) == FileType.systemverilog:
            cmd += ["-sv"]
        if flags:  # pragma: no cover
            cmd += flags

        cmd += [path.name]

        self._logger.info("verilator command line: '%s'", cmd)
        return runShellCommand(cmd)
