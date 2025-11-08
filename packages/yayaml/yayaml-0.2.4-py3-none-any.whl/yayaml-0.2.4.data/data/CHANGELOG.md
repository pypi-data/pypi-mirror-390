# Changelog

`yayaml` aims to adhere to [semantic versioning](https://semver.org/).

## v0.2.4
- !9 add test job for Python 3.14.
- !9 adds the `!len` YAML tag; usage: `!len [obj]`, where obj can be a sequence or mapping.


## v0.2.3
- !8 adds the `!oneline` / `!collapse-whitespace` tags to produce one-line strings from multi-line YAML string specifications.


## v0.2.2
- !7 version and documentation upgrades.


## v0.2.1
- !6 removes restriction on supported numpy version.


## v0.2.0
- !5 changes the default encoding in `load_yml` to UTF-8, falling back to the OS-default if it does not work.
- !5 adds the following new constructors:
    - `!env` as alias for `!getenv`.
    - `!getboolenv`/`!boolenv` evaluates an environment variable as a boolean.
    - `!if-else` evaluates simple conditionals.
    - `!if-windows-else` and `!if-unix-else` allow specifying platform-specific conditionals.
- !5 removes deprecated `yaml_unsafe` loader


## v0.1.1
- !1 changes module names to no longer be prefixed with `_`.


## v0.1.0

This initial version moves the YAML-related tools that were integrated into the [paramspace](https://gitlab.com/blsqr/paramspace) package (prior to its 2.6 release) into this new package named `yayaml`.

yay :)

Specifically, it is based on code from commit [`7b1d2e7`](https://gitlab.com/blsqr/paramspace/-/commit/7b1d2e7e44fe38dadb0e6af901d72299b1ed6dd0), but already makes a number of abstractions and improvements.
