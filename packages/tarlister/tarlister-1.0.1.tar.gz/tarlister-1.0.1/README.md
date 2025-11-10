# tarlister

This is just a quick tool to read the first few entries from an archive (or
tape), as long the archive type is supported by
[libarchive](https://www.libarchive.org). And there's
[many](https://github.com/libarchive/libarchive/wiki/LibarchiveFormats); if
your archive is supported by `bsdtar`, it is almost surely supported by this
tool. 

## Running

Just run it with `-n 10` to give you the first 10 file names contained in an archive:

```shell
tarlister -n 10 /dev/foo.tar.xz
```


## Installation

Uses [`uv`](https://docs.astral.sh/uv/) for building
```shell
uv install .
```

you can use `uv` or `pip` to install:

```shell
pip install tarlister
```

or run directly from the package

```shell
uvx tarlister --help
```

## But why?

[That's why.](https://unix.stackexchange.com/a/801135/106650)
