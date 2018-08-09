"""
Common shell operations
-----------------------
"""
import pathlib
import typing
import tbot
from tbot import config
from tbot import tc


@tbot.testcase
def setup_tftpdir(
    tb: tbot.TBot,
    *,
    root: typing.Optional[pathlib.PurePosixPath] = None,
    subdir: typing.Optional[pathlib.PurePosixPath] = None,
) -> tc.TftpDirectory:
    """
    Setup the tftp directory

    :param pathlib.PurePosixPath root: Optional path to the TFTP root directory, defaults to
                    ``tb.config["tftp.root"]``
    :param pathlib.PurePosixPath subdir: Optional subdir path inside the TFTP directory (has a
                   default value in ``config/tbot.py``)
    :returns: The TFTP directory as a meta object
    :rtype: TftpDirectory
    """
    root = root or tb.config["tftp.root"]
    subdir = subdir or tb.config["tftp.directory"]

    if not isinstance(root, pathlib.PurePosixPath):
        raise config.InvalidConfigException("'tftp.root' must be a PurePosixPath!")
    if not isinstance(subdir, pathlib.PurePosixPath):
        raise config.InvalidConfigException("'tftp.directory' must be a PurePosixPath!")

    tftpdir = tc.TftpDirectory(root, subdir)

    tb.shell.exec0(f"mkdir -p {tftpdir.path}", log_show=False)

    tbot.log.debug(f"TFTP directory is '{tftpdir.path}'")

    return tftpdir


@tbot.testcase
def cp_to_tftpdir(
    tb: tbot.TBot,
    *,
    source: pathlib.PurePosixPath,
    dest_name: typing.Optional[str] = None,
    tftpdir: tc.TftpDirectory,
) -> None:
    dest_path = tftpdir.path / (source.name if dest_name is None else dest_name)

    tbot.log.debug(f"Copying '{source}' to '{dest_path}'")

    tb.shell.exec0(f"cp {source} {dest_path}")


@tbot.testcase
def retrieve_build_artifact(
    tb: tbot.TBot,
    *,
    buildfile: pathlib.PurePosixPath,
    buildhost: typing.Optional[str] = None,
    scp_flags: typing.Optional[str] = None,
    scp_address: typing.Optional[str] = None,
) -> pathlib.PurePosixPath:
    """
    Copy artifacts from the buildhost to the labhost

    :param pathlib.PurePosixPath buildfile: File on the buildhost
    :param str buildhost: Name of the buildhost if you do not want to use
                          the default
    :param str scp_flags: SCP flags to be added to scp commands, defaults to
                          ``tb.config["build.<name>.scp_flags"]``
    :param str scp_address: Address of the form ``<user>@<host>``
                            of the buildhost, defaults to
                            \
``tb.config["build.<name>.username"]+"@"+tb.config["build.<name>.hostname"]``
    :returns: Path where the file has been copied
    :rtype: pathlib.PurePosixPath
    """
    buildhost = buildhost or tb.config["build.default", "<missing>"]
    bhcfg = f"build.{buildhost}."
    scp_flags = scp_flags or tb.config[bhcfg + "scp_flags", ""]
    scp_address = (
        scp_address
        or tb.config[bhcfg + "username"] + "@" + tb.config[bhcfg + "hostname"]
    )

    destination = tb.config["tbot.artifactsdir"] / buildfile.name
    if not isinstance(destination, pathlib.PurePosixPath):
        raise config.InvalidConfigException(
            "'tbot.artifactsdir' must be a PurePosixPath"
        )
    tbot.log.debug(f"cp {buildfile} (build) -> {destination} (lab)")

    tb.machines["labhost-noenv"].exec0(f"mkdir -p {destination.parent}", log_show=False)
    tb.machines["labhost-noenv"].exec0(
        f"scp {scp_flags} {scp_address}:{buildfile} {destination}", log_show=False
    )

    return destination
