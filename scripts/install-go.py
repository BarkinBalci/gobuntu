#!/usr/bin/env python3
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from typing import NoReturn

GO_RELEASES_URL = "https://go.dev/dl/?mode=json&include=all"


def fail(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    sys.exit(1)


def go_arch(target_arch: str) -> str:
    aliases = {
        "amd64": "amd64",
        "x86_64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "arm": "armv6l",
        "armv6l": "armv6l",
        "armv7l": "armv6l",
    }
    try:
        return aliases[target_arch]
    except KeyError:
        fail(f"Unsupported Go architecture: {target_arch}")


def load_releases() -> list[dict]:
    with urllib.request.urlopen(GO_RELEASES_URL, timeout=30) as response:
        return json.load(response)


def resolve_version(requested: str, releases: list[dict]) -> str:
    if re.fullmatch(r"go\d+\.\d+\.\d+", requested):
        return requested
    if re.fullmatch(r"\d+\.\d+\.\d+", requested):
        return f"go{requested}"
    if not re.fullmatch(r"\d+\.\d+", requested):
        fail("GO_VERSION must be a minor version like 1.26 or a patch version like 1.26.3")

    versions = []
    for release in releases:
        match = re.fullmatch(r"go(\d+)\.(\d+)\.(\d+)", release["version"])
        if match and f"{match[1]}.{match[2]}" == requested:
            versions.append((int(match[3]), release["version"]))

    if not versions:
        fail(f"No Go release found for {requested}")
    return max(versions)[1]


def find_file(releases: list[dict], version: str, filename: str) -> dict:
    for release in releases:
        if release["version"] == version:
            for file in release["files"]:
                if file["filename"] == filename:
                    return file
    fail(f"No Go download found for {filename}")


def download(url: str, destination: str) -> None:
    with urllib.request.urlopen(url, timeout=120) as response, open(destination, "wb") as output:
        shutil.copyfileobj(response, output)


def verify_sha256(path: str, expected: str) -> None:
    with open(path, "rb") as archive:
        digest = hashlib.file_digest(archive, "sha256").hexdigest()
    if digest != expected:
        fail(f"Checksum mismatch for {path}: expected {expected}, got {digest}")


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: install-go.py <go-version>")

    requested = sys.argv[1]

    releases = load_releases()
    version = resolve_version(requested, releases)
    filename = f"{version}.linux-{go_arch(platform.machine())}.tar.gz"
    file = find_file(releases, version, filename)
    archive = f"/tmp/{filename}"

    download(f"https://go.dev/dl/{filename}", archive)
    verify_sha256(archive, file["sha256"])

    shutil.rmtree("/usr/local/go", ignore_errors=True)
    with tarfile.open(archive) as tar:
        tar.extractall("/usr/local")

    subprocess.run(["/usr/local/go/bin/go", "version"], check=True)


if __name__ == "__main__":
    main()
