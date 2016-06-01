from pytest import raises

import jiffybox.cli


def test_invocation(capsys):
    with raises(SystemExit) as e:
        jiffybox.cli.jiffybox(['--help'])
    assert e.value.code == 0
