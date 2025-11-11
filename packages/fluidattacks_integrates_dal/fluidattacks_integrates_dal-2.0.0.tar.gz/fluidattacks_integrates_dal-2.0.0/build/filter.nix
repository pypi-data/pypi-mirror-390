path_filter: src:
path_filter {
  root = src;
  include = [
    "fluidattacks_integrates_dal"
    "tests"
    "pyproject.toml"
    "mypy.ini"
    "ruff.toml"
    "uv.lock"
  ];
}
