import shlex

from ... import __version__


def test_cli_version(script_runner):
    cmd = "arrakis --version"
    result = script_runner.run(shlex.split(cmd))
    assert result.stdout.rstrip() == __version__


def test_cli_help(script_runner):
    cmd = "arrakis --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    cmd = "arrakis count --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    cmd = "arrakis describe --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    cmd = "arrakis find --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    cmd = "arrakis publish --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    cmd = "arrakis stream --help"
    result = script_runner.run(shlex.split(cmd))
    assert result.success
