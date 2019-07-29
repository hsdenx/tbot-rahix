import getpass
import typing
import contextlib
import tbot
from tbot.machine import linux, connector


class MiniSSHMachine(connector.SSHConnector, linux.Bash):
    """SSHMachine for test purposes."""

    hostname = "localhost"
    name = "minissh-local"
    # This would work as well, but we need to test ssh_config somewhere ...
    # ignore_hostkey = True
    ssh_config = ["StrictHostKeyChecking=no"]

    @property
    def username(self) -> str:
        return self._username

    @property
    def port(self) -> int:
        return self._port

    @property
    def workdir(self) -> "linux.Path[MiniSSHMachine]":
        """Return a workdir."""
        return linux.Workdir.static(self, "/tmp/tbot-wd/minisshd-remote")

    def __init__(self, labhost: linux.LabHost, port: int) -> None:
        """Create a new MiniSSHMachine."""
        self._port = port
        self._username = labhost.env("USER")

        super().__init__(labhost)


class MiniSSHLabHost(connector.ParamikoConnector, linux.Bash):
    hostname = "localhost"
    name = "minissh-lab"
    ignore_hostkey = True

    @property
    def username(self) -> str:
        return self._username

    @property
    def port(self) -> int:
        return self._port

    @property
    def workdir(self) -> "linux.Path[MiniSSHLabHost]":
        """Return a workdir."""
        return linux.Workdir.static(self, "/tmp/tbot-wd/minisshd-remote")

    def __init__(self, port: int) -> None:
        """Create a new MiniSSHMachine."""
        self._port = port
        self._username = getpass.getuser()

        super().__init__()


@tbot.testcase
def check_minisshd(h: linux.LabHost) -> bool:
    """Check if this host can run a minisshd."""
    return h.test("which", "dropbear")


@tbot.testcase
@contextlib.contextmanager
def minisshd(h: linux.LabHost, port: int = 2022) -> typing.Generator:
    """
    Create a new minisshd server and machine.

    Intended for use in a ``with``-statement::

        if check_minisshd(lh):
            with minisshd(lh) as ssh:
                ssh.exec0("uname", "-a")

    :param linux.LabHost h: lab-host
    :param int port: Port for the ssh server, defaults to ``2022``.
    :rtype: MiniSSHMachine
    """
    server_dir = h.workdir / "minisshd"
    h.exec0("mkdir", "-p", server_dir)

    key_file = server_dir / "ssh_host_key"
    pid_file = server_dir / "dropbear.pid"

    # Create host key
    if not key_file.exists():
        h.exec0("dropbearkey", "-t", "rsa", "-f", key_file)

    h.exec0("dropbear", "-p", "127.0.0.1:2022", "-r", key_file, "-P", pid_file)

    # Try reading the file again if it does not yet exist
    for i in range(10):
        ret, pid = h.exec("cat", pid_file)
        if ret == 0:
            pid = pid.strip()
            break
    else:
        raise RuntimeError("dropbear did not create a pid-file!")

    try:
        with MiniSSHMachine(h, port) as ssh_machine:
            yield ssh_machine
    finally:
        tbot.log.message("Stopping dropbear ...")
        h.exec0("kill", pid)
