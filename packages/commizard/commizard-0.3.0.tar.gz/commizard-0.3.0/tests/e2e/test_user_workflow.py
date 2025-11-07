"""
The tests in this file assume that:
1. git is installed
2. we are inside a git working tree (in the git repo, not the .git folder)
"""

import os
import subprocess

import pytest

# Don't mess up the encoding of colored output
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.parametrize(
    "user_in",
    [
        ["       quit            ", "start", "list"],
        ["exit", "quit", "quit"],
        [" exit", "     gen", "doesn't exist", "shouldn't even execute"],
    ],
)
def test_early_exit(user_in):
    user_in = "\n".join(user_in) + "\n"
    out = subprocess.run(
        ["commizard"],
        capture_output=True,
        input=user_in.encode(),
        timeout=5,
        env=env,
    )
    assert out.returncode == 0
    assert out.stderr.decode("utf-8").strip() == ""


@pytest.mark.parametrize(
    "user_in",
    [
        ["clear", "list", "start something", "gen", "exit"],
        ["start something", "gen", "quit"],
        ["gen", "quit"],
    ],
)
def test_correct_workflow(user_in):
    user_in = "\n".join(user_in) + "\n"
    out = subprocess.run(
        ["commizard"], capture_output=True, input=user_in.encode(), env=env
    )
    assert out.returncode == 0
