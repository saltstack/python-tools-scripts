import os
import shutil
import gzip
import pathlib
import tempfile
import tarfile
import nox
from nox.command import CommandFailed

COVERAGE_VERSION_REQUIREMENT = "coverage==6.2"

# Be verbose when running under a CI context
PIP_INSTALL_SILENT = (os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")) is None
CI_RUN = PIP_INSTALL_SILENT is False
SKIP_REQUIREMENTS_INSTALL = "SKIP_REQUIREMENTS_INSTALL" in os.environ
EXTRA_REQUIREMENTS_INSTALL = os.environ.get("EXTRA_REQUIREMENTS_INSTALL")

# Paths
REPO_ROOT = pathlib.Path(__file__).resolve().parent
# Change current directory to REPO_ROOT
os.chdir(str(REPO_ROOT))


@nox.session(name="twine-check", python="3")
def twine_check(session):
    """
    Run ``twine-check`` against the source distribution package.
    """
    build(session)
    session.run("twine", "check", "dist/*")


@nox.session(name="changelog", python="3")
@nox.parametrize("draft", [False, True])
def changelog(session, draft):
    """
    Generate changelog.
    """
    session.install("--progress-bar=off", "-e", ".[changelog]", silent=PIP_INSTALL_SILENT)

    version = session.run(
        "python",
        "setup.py",
        "--version",
        silent=True,
        log=False,
        stderr=None,
    ).strip()

    town_cmd = ["towncrier", "build", f"--version={version}"]
    if draft:
        town_cmd.append("--draft")
    session.run(*town_cmd)


@nox.session(name="release")
def release(session):
    """
    Create a release tag.
    """
    if not session.posargs:
        session.error(
            "Forgot to pass the version to release? For example `nox -e release -- 1.1.0`"
        )
    if len(session.posargs) > 1:
        session.error(
            "Only one argument is supported by the `release` nox session. "
            "For example `nox -e release -- 1.1.0`"
        )
    version = session.posargs[0]
    try:
        session.log("Generating temporary %s tag", version)
        session.run("git", "tag", "-as", version, "-m", f"Release {version}", external=True)
        changelog(session, draft=False)
    except CommandFailed:
        session.error("Failed to generate the temporary tag")
    # session.notify("changelog(draft=False)")
    try:
        session.log("Generating the release changelog")
        session.run(
            "git",
            "commit",
            "-a",
            "-m",
            f"Generate Changelog for version {version}",
            external=True,
        )
    except CommandFailed:
        session.error("Failed to generate the release changelog")
    try:
        session.log("Overwriting temporary %s tag", version)
        session.run("git", "tag", "-fas", version, "-m", f"Release {version}", external=True)
    except CommandFailed:
        session.error("Failed to overwrite the temporary tag")
    session.warn("Don't forget to push the newly created tag")


class Recompress:
    """
    Helper class to re-compress a ``.tag.gz`` file to make it reproducible.
    """

    def __init__(self, mtime):
        self.mtime = int(mtime)

    def tar_reset(self, tarinfo):
        """
        Reset user, group, mtime, and mode to create reproducible tar.
        """
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        tarinfo.mtime = self.mtime
        if tarinfo.type == tarfile.DIRTYPE:
            tarinfo.mode = 0o755
        else:
            tarinfo.mode = 0o644
        if tarinfo.pax_headers:
            raise ValueError(tarinfo.name, tarinfo.pax_headers)
        return tarinfo

    def recompress(self, targz):
        """
        Re-compress the passed path.
        """
        tempd = pathlib.Path(tempfile.mkdtemp()).resolve()
        d_src = tempd.joinpath("src")
        d_src.mkdir()
        d_tar = tempd.joinpath(targz.stem)
        d_targz = tempd.joinpath(targz.name)
        with tarfile.open(d_tar, "w|") as wfile:
            with tarfile.open(targz, "r:gz") as rfile:
                rfile.extractall(d_src)
                extracted_dir = next(pathlib.Path(d_src).iterdir())
                for name in sorted(extracted_dir.rglob("*")):
                    wfile.add(
                        str(name),
                        filter=self.tar_reset,
                        recursive=False,
                        arcname=str(name.relative_to(d_src)),
                    )

        with open(d_tar, "rb") as rfh:
            with gzip.GzipFile(
                fileobj=open(d_targz, "wb"), mode="wb", filename="", mtime=self.mtime
            ) as gz:
                while True:
                    chunk = rfh.read(1024)
                    if not chunk:
                        break
                    gz.write(chunk)
        targz.unlink()
        shutil.move(str(d_targz), str(targz))


@nox.session(python="3")
def build(session):
    """
    Build source and binary distributions based off the current commit author date UNIX timestamp.

    The reason being, reproducible packages.
    .. code-block: shell
        git show -s --format=%at HEAD
    """
    shutil.rmtree("dist/", ignore_errors=True)
    session.install("--progress-bar=off", "-r", "requirements/build.txt", silent=PIP_INSTALL_SILENT)

    timestamp = session.run(
        "git",
        "show",
        "-s",
        "--format=%at",
        "HEAD",
        silent=True,
        log=False,
        stderr=None,
    ).strip()
    env = {"SOURCE_DATE_EPOCH": str(timestamp)}
    session.run(
        "python",
        "-m",
        "build",
        "--sdist",
        "--wheel",
        str(REPO_ROOT),
        env=env,
    )
    # Recreate sdist to be reproducible
    recompress = Recompress(timestamp)
    for targz in REPO_ROOT.joinpath("dist").glob("*.tar.gz"):
        session.log("Re-compressing %s...", targz.relative_to(REPO_ROOT))
        recompress.recompress(targz)

    sha256sum = shutil.which("sha256sum")
    if sha256sum:
        packages = [str(pkg.relative_to(REPO_ROOT)) for pkg in REPO_ROOT.joinpath("dist").iterdir()]
        session.run("sha256sum", *packages, external=True)
    session.run("python", "-m", "twine", "check", "dist/*")
