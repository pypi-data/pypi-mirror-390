# ipe_servicehub_protos

This repository contains the [Protocol Buffer](https://protobuf.dev/) files for communication between the [SDR Userspace Drivers](https://gitlab.kit.edu/kit/ipe-sdr/ipe-sdr-dev/software/sdr_userspace_drivers) and client applications such as the [qiclib](https://gitlab.kit.edu/kit/ipe-sdr/ipe-sdr-dev/software/qiclib) or [cirque](https://gitlab.kit.edu/kit/ipe-sdr/ipe-sdr-dev/software/cirque).

## Python Bindings

To automatically build bindings, add `ipe_servicehub_protos` as submodule to your main module.
Example:

```tree
example_package
├── ipe_servicehub_protos
│   ├── build_protos.py
│   └── README.md
└── src
    └── example_package
        └── __init__.py
```

Then, in your pyproject.toml, add the following configuration settings (if they don't exist already):
```toml
[build-system]
requires = ["hatchling>=1.25", "hatch-vcs>=0.4", "grpcio-tools==1.73.1"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.custom]
path = "path/to/ipe_servicehub_protos/python/build_protos.py"
out_dir = "path/to/output/"
```

Make sure to
1. Replace `path/to/ipe_servicehub_protos` with the actual path to the submodule. For the example above, this would simply be `ipe_servicehub_protos`
2. Replace `path/to/output/` with the actual path where you want to install the protos to. This also defines the package name.
  For example, if `path/to/output/` is `src/example_package/protos`, the generated methods can be imported using `example_package.protos.proto_file_pb2`

## C++ Bindings
The C++ bindings only work when this module is used as submodule of [sdr_userspace_drivers](https://gitlab.kit.edu/kit/ipe-sdr/ipe-sdr-dev/software/sdr_userspace_drivers).

To add a new `.proto` file, use `SdrAddProtoLibraryWithCommonDatatypes` and pass the file name without the `.proto` ending. For example:

```cmake
# Add foo.proto
SdrAddProtoLibraryWithCommonDatatypes(foo)
```

This will add a cmake target called `foo` that contains all necessary C++ headers and source files.

## Documentation

Requirements are:

* git (optional)
* doxygen( required)
* python (required)

The interface documentation can be created by:

```bash
cd doc/
./create_docs
```

Afterwards the `index.html`, located in `doc/html/` can be opened with a browser [click](doc/html/index.html).
