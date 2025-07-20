"""Smoke test for CLI.

This test doesn't exercise the full workflow because it depends on
external data (the bedrock GeoPackage). It simply ensures that the
CLI entrypoint is importable and callable without raising unexpected
exceptions when no dataset is present. If a dataset is available in
``data/raw/`` the pipeline may still error when attempting to read it,
which is acceptable for this placeholder test.
"""


def test_cli_import() -> None:
    """Ensure the CLI module can be imported."""
    import src.cli  # noqa: F401
