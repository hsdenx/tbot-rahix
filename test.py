import tbot
from tbot.machine import linux


@tbot.testcase
def cat_file(f: linux.Path) -> str:
    return f.host.exec0("cat", f)


@tbot.testcase
def test_devel() -> None:
    from config.labs import dummy
    with dummy.DummyLab() as lh:
        v = cat_file(linux.Path(lh, "/proc/version")).strip()
        tbot.log.message(f"Version: {v}")

        f = linux.Path(lh, lh.workdir / "myfile.txt")
        lh.exec0("uname", "-n", stdout=f)

        name = cat_file(f).strip()
        tbot.log.message(f"Name: {name}")

    try:
        class MyException(Exception):
            pass

        @tbot.testcase
        def failing() -> None:
            raise MyException()

        failing()
    except MyException:
        pass


@tbot.testcase
def test_channel_use() -> None:
    from tbot.machine.channel import subprocess
    from config.labs import dummy
    # chan = paramiko.ParamikoChannel(lh._obtain_channel())
    chan = subprocess.SubprocessChannel()
    tbot.log.message(repr(chan))

    o = chan.raw_command("dmesg")

    chan.close()


if __name__ == "__main__":
    test_channel_use()
