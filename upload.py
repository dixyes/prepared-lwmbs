#!/usr/bin/env python3
import argparse
import os
import subprocess
from typing import Optional

LWMBS_REPO = os.getenv("LWMBS_REPO", "https://github.com/dixyes/lwmbs")
LWMBS_BRANCH = os.getenv("LWMBS_BRANCH", "master")
IMAGE_NAME = os.getenv("IMAGE_NAME", "dixyes/prepared-lwmbs")
IMAGE_NAME_GHCR = os.getenv("IMAGE_NAME_GHCR", f"ghcr.io/{IMAGE_NAME}")

PHP_VERSION = "8.2"

if os.environ.get("CI"):
    IMAGE_NAME_CHECK = IMAGE_NAME_GHCR
    CENTOS_MIRROR = "https://mirror.facebook.net/centos/"
    EPEL_MIRROR = "https://mirror.facebook.net/fedora/epel/"
    SCLO_MIRROR = "https://mirror.facebook.net/centos/7/sclo/"
    GNU_MIRROR = "https://mirror.facebook.net/gnu/"
    FEDORA_MIRROR = "https://mirror.facebook.net/fedora/linux/"
    # FEDORA_MIRROR = ""
    CENTOS_ALTARCH_MIRROR = "https://mirror.facebook.net/centos-altarch/"
else:
    IMAGE_NAME_CHECK = IMAGE_NAME
    CENTOS_MIRROR = "https://mirrors.ustc.edu.cn/centos/"
    EPEL_MIRROR = "https://mirrors.ustc.edu.cn/epel/"
    SCLO_MIRROR = "https://mirrors.ustc.edu.cn/centos/7/sclo/"
    GNU_MIRROR = "https://mirrors.ustc.edu.cn/gnu/"
    FEDORA_MIRROR = "https://mirrors.ustc.edu.cn/fedora/"
    CENTOS_ALTARCH_MIRROR = "https://mirrors.ustc.edu.cn/centos-altarch/"

types = {
    "linux-glibc-x86_64": {
        "CENTOS_MIRROR": CENTOS_MIRROR,
        "EPEL_MIRROR": EPEL_MIRROR,
        "SCLO_MIRROR": SCLO_MIRROR,
        "GNU_MIRROR": GNU_MIRROR,
    },
    "linux-glibc-aarch64": {
        "FEDORA_MIRROR": FEDORA_MIRROR,
        "CENTOS_ALTARCH_MIRROR": CENTOS_ALTARCH_MIRROR,
    },
}

BUILD_CMD = ("buildx", "build")


def getSrcHash(image: str = f"{IMAGE_NAME_CHECK}:linux-glibc-x86_64") -> Optional[str]:
    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            *(
                ["-e", f"GITHUB_TOKEN={githubToken}"]
                if (githubToken := os.getenv("GITHUB_TOKEN"))
                else []
            ),
            *(
                ["-e", f"GITHUB_USER={githubUser}"]
                if (githubUser := os.getenv("GITHUB_USER"))
                else []
            ),
            image,
            "php",
            "/lwmbs/fetch_source.php",
            "--hash",
            "",
            "",
        ],
        stdout=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None
    else:
        return proc.stdout.decode().strip()


def buildBaseImage(typ: str, buildArgs: list[str]):
    global lwmbsRevision

    cmd = [
        "docker",
        *BUILD_CMD,
    ]

    for arg, value in buildArgs.items():
        cmd.extend(["--build-arg", f"{arg}={value}"])

    cmd.extend(
        [
            ".",
            "-f",
            f"Dockerfile.{typ}",
            "-t",
            f"{IMAGE_NAME}:{typ}",
        ]
    )

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("build image failed")

    for tag in (
        f"{IMAGE_NAME}:{typ}-{lwmbsRevision}",
        f"{IMAGE_NAME_GHCR}:{typ}",
        f"{IMAGE_NAME_GHCR}:{typ}-{lwmbsRevision}",
    ):
        proc = subprocess.run(
            [
                "docker",
                "tag",
                f"{IMAGE_NAME}:{typ}",
                tag,
            ]
        )
        if proc.returncode != 0:
            raise RuntimeError(f"tag image {tag} failed")

        proc = subprocess.run(["docker", "push", tag])
        if proc.returncode != 0:
            raise RuntimeError(f"push image {tag} failed")


def buildSrcImage(typ: str, phpVersion: str):
    proc = subprocess.run(
        [
            "docker",
            *BUILD_CMD,
            ".",
            "-t",
            f"{IMAGE_NAME}:{typ}-src",
            "-f",
            f"Dockerfile.src",
            "--build-arg",
            f"PHP_VERSION={phpVersion}",
            "--build-arg",
            f"BASE_TAG={typ}",
            *(
                ["--build-arg", f"GITHUB_TOKEN={githubToken}"]
                if (githubToken := os.getenv("GITHUB_TOKEN"))
                else []
            ),
            *(
                ["--build-arg", f"GITHUB_USER={githubUser}"]
                if (githubUser := os.getenv("GITHUB_USER"))
                else []
            ),
        ]
    )
    if proc.returncode != 0:
        raise RuntimeError("build image failed")

    srcHash = getSrcHash(f"{IMAGE_NAME}:{typ}-src")

    for tag in (
        f"{IMAGE_NAME}:{typ}-src-{srcHash}",
        f"{IMAGE_NAME_GHCR}:{typ}-src",
        f"{IMAGE_NAME_GHCR}:{typ}-src-{srcHash}",
    ):
        proc = subprocess.run(
            [
                "docker",
                "tag",
                f"{IMAGE_NAME}:{typ}-src",
                tag,
            ]
        )
        if proc.returncode != 0:
            raise RuntimeError(f"tag image {tag} failed")

        proc = subprocess.run(["docker", "push", tag])
        if proc.returncode != 0:
            raise RuntimeError(f"push image {tag} failed")


def mian():
    global lwmbsRevision

    parser = argparse.ArgumentParser()
    parser.add_argument("--override", help="overrides images", action="store_true")

    args = parser.parse_args()

    proc = subprocess.run(
        ["git", "ls-remote", LWMBS_REPO, LWMBS_BRANCH], stdout=subprocess.PIPE
    )
    if proc.returncode != 0:
        raise RuntimeError("git ls-remote failed")
    lwmbsRevision = proc.stdout.decode().strip().split()[0]

    # print(lwmbsRevision)
    srcHash = getSrcHash()

    for typ, buildArgs in types.items():
        baseRebuilt = False
        proc = subprocess.run(
            [
                "docker",
                "manifest",
                "inspect",
                f"{IMAGE_NAME_CHECK}:{typ}-{lwmbsRevision}",
            ]
        )
        if proc.returncode != 0 or args.override:
            baseRebuilt = True
            buildBaseImage(typ=typ, buildArgs=buildArgs)

        if srcHash:
            proc = subprocess.run(
                [
                    "docker",
                    "manifest",
                    "inspect",
                    f"{IMAGE_NAME_CHECK}:{typ}-src-{srcHash}",
                ]
            )
            if baseRebuilt or proc.returncode != 0:
                # for phpVersion in PHP_VERSIONS:
                # buildSrcImage(typ=typ, phpVersion=phpVersion)
                buildSrcImage(typ=typ, phpVersion=PHP_VERSION)


if "__main__" == __name__:
    mian()
