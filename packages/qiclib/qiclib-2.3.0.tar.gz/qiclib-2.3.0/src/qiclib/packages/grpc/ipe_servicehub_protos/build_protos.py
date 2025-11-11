# Copyright © 2017-2023 Quantum Interface (quantuminterface@ipe.kit.edu)
# Lukas Scheller, IPE, Karlsruhe Institute of Technology
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
This is a [hatchling build hook](https://hatch.pypa.io/1.7/plugins/build-hook/custom/#pyprojecttoml)
to automatically generate python grpc bindings for protobuf files.
"""
import re
import shutil
import sys
from io import StringIO

import grpc_tools.protoc
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def _get_resource_file_name(package_or_requirement: str, resource_name: str) -> str:
    """Get the filename for a resource on the file system."""
    if sys.version_info >= (3, 9, 0):
        from importlib import resources

        file_name = (resources.files(package_or_requirement) / resource_name).resolve()
    else:
        import pkg_resources

        file_name = pkg_resources.resource_filename(
            package_or_requirement, resource_name
        )
    return str(file_name)

def _patch_generated_grpc_file(path_to_file: Path, package: str):
    """
    Patches the generated GRPC file by appending the package name to the generated protobuf file.
    This is suboptimal as the patching might have unwanted side effects, but this seems to be the only viable solution
    See also [this discussion](https://github.com/protocolbuffers/protobuf/issues/1491) on GitHub for a better understanding.
    """
    patched = StringIO()
    with open(path_to_file, "r", encoding="utf-8") as infile:
        for line in infile:
            if match := re.search(r"^import ([\w_]+)_pb2 as ([\w_]+)$", line):
                module_name = match.group(1)
                imported_module_name = match.group(2)
                patched.write(
                    f"import {package}.{module_name}_pb2 as {imported_module_name}\n"
                )
            elif match := re.search(r"^from ([\w_]+)_pb2 import (.*)$", line):
                module_name = match.group(1)
                imported_stuff = match.group(2)
                patched.write(
                    f"from {package}.{module_name}_pb2 import {imported_stuff}\n"
                )
            else:
                patched.write(line)
    with open(path_to_file, "w", encoding="utf-8") as outfile:
        patched.seek(0)
        shutil.copyfileobj(patched, outfile)


def out_dir_to_package_name(out_dir: str):
    parts = Path(out_dir).parts
    if parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)

class BuildProtos(BuildHookInterface):
    description = "build grpc protobuf modules"

    def initialize(self, _version, _build_data):
        # protos_root points to the `ipe_servicehub_protos` folder
        protos_root = Path(__file__).parent

        # out_dir is where the generated files will be populated
        # If defined through the config, it is given as a path
        # relative to the directory that the pyproject.toml file resides in.
        # Example config:
        #
        # ... # other, project-specific configurations
        # 
        # [tool.hatch.build.hooks.custom]
        # path = "path/to/ipe_servicehub_protos/python/build_protos.py"
        # out_dir = "path/to/output/"
        relative_out_dir: str = self.config.get("out_dir", "src/ipe_servicehub_protos")
        out_dir = Path(self.root) / relative_out_dir

        package_name = out_dir_to_package_name(relative_out_dir)

        # These are builtin proto files, such as `google/protobuf/empty` that are included by other proto files
        well_known_protos_include = _get_resource_file_name("grpc_tools", "_proto")
        # Iterate through all the proto files in this repository
        for file in protos_root.iterdir(): # type: Path
            if file.suffix != ".proto":
                continue
            command = [
                "grpc_tools.protoc",
                f"--proto_path={well_known_protos_include}",
                f"--proto_path={protos_root}",
                f"--python_out={out_dir}",
                f"--grpc_python_out={out_dir}",
                f"--pyi_out={out_dir}",
                str(file.name),
            ]
            if (ret_code := grpc_tools.protoc.main(command)) != 0:
                raise Exception(
                    f"Command returned with non-zero exit code 0 ({ret_code})"
                )
            stem = file.stem
            _patch_generated_grpc_file(out_dir / (stem + "_pb2.py"), package_name)
            _patch_generated_grpc_file(out_dir / (stem + "_pb2_grpc.py"), package_name)
            _patch_generated_grpc_file(out_dir / (stem + "_pb2.pyi"), package_name)
