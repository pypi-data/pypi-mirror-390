import subprocess

import pytest


@pytest.mark.parametrize(
    "arg",
    [
        "-v",
        "--version",
        "-h",
        "--help",
    ],
)
def test_arg(arg):
    out = subprocess.run(  # noqa: S603
        ["commizard", arg], capture_output=True, text=True
    )
    assert out.returncode == 0
    assert out.stderr.strip() == ""
