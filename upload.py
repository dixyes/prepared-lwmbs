#!/usr/bin/env pyhon3
import os
import subprocess

if os.environ.get("CI"):
    CENTOS_MIRROR = "https://mirror.facebook.net/centos/"
    EPEL_MIRROR = "https://mirror.facebook.net/fedora/epel/"
    SCLO_MIRROR = "https://mirror.facebook.net/centos/7/sclo/"
    GNU_MIRROR = "https://mirror.facebook.net/gnu/"
    FEDORA_MIRROR = "https://mirror.facebook.net/fedora/linux/"
    CENTOS_ALTARCH_MIRROR = "https://mirror.facebook.net/centos-altarch/"
else:
    CENTOS_MIRROR = "https://mirrors.ustc.edu.cn/centos/"
    EPEL_MIRROR = "https://mirrors.ustc.edu.cn/epel/"
    SCLO_MIRROR = "https://mirrors.ustc.edu.cn/centos/7/sclo/"
    GNU_MIRROR = "https://mirrors.ustc.edu.cn/gnu/"
    FEDORA_MIRROR = "https://mirrors.ustc.edu.cn/fedora/"
    CENTOS_ALTARCH_MIRROR = "https://mirrors.ustc.edu.cn/centos-altarch/"


LWMBS_REPO = os.getenv("LWMBS_REPO", "https://github.com/dixyes/lwmbs")
LWMBS_BRANCH = os.getenv("LWMBS_BRANCH", "master")
IMAGE_NAME = os.getenv("IMAGE_NAME", "dixyes/prepared-lwmbs")

PHP_VERSIONS = (
    "80",
    "81",
    "82",
)

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


def buildBaseImage(typ: str, buildArgs: list[str]):
    global scriptsRevision
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

    cmd = [
        "docker",
        "tag",
        f"{IMAGE_NAME}:{typ}",
        f"{IMAGE_NAME}:{typ}-{scriptsRevision}-{lwmbsRevision}",
    ]

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("tag image failed")

    cmd = [
        "docker",
        "push",
        f"{IMAGE_NAME}:{typ}",
    ]

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("push image failed")

    cmd = [
        "docker",
        "push",
        f"{IMAGE_NAME}:{typ}-{scriptsRevision}-{lwmbsRevision}",
    ]

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("push image failed")


def buildSrcImage(typ: str, phpVersion: str):
    global srcHash
    proc = subprocess.run(
        [
            "docker",
            *BUILD_CMD,
            ".",
            "-t",
            f"{IMAGE_NAME}:{typ}-src-{srcHash}",
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

    cmd = ["docker", "push", f"{IMAGE_NAME}:{typ}-src-{srcHash}"]

    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("push image failed")


def mian():
    global scriptsRevision
    global lwmbsRevision
    global srcHash

    proc = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError("git rev-parse HEAD failed")
    scriptsRevision = proc.stdout.decode().strip()

    proc = subprocess.run(
        ["git", "ls-remote", LWMBS_REPO, LWMBS_BRANCH], stdout=subprocess.PIPE
    )
    if proc.returncode != 0:
        raise RuntimeError("git ls-remote failed")
    lwmbsRevision = proc.stdout.decode().strip().split()[0]

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
            f"{IMAGE_NAME}:linux-glibc-x86_64",
            "php",
            "/lwmbs/fetch_source.php",
            "--hash",
            "",
            "",
        ],
        stdout=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError("get source hash")
    srcHash = proc.stdout.decode().strip()

    # print(scriptsRevision, lwmbsRevision)

    for typ, args in types.items():
        baseRebuilt = False
        proc = subprocess.run(
            [
                "docker",
                "manifest",
                "inspect",
                f"{IMAGE_NAME}:{typ}-{scriptsRevision}-{lwmbsRevision}",
            ]
        )
        if proc.returncode != 0:
            baseRebuilt = True
            buildBaseImage(typ=typ, buildArgs=args)

        proc = subprocess.run(
            [
                "docker",
                "manifest",
                "inspect",
                f"{IMAGE_NAME}:{typ}-src-{srcHash}",
            ]
        )
        if baseRebuilt or proc.returncode != 0:
            for phpVersion in PHP_VERSIONS:
                buildSrcImage(typ=typ, phpVersion=phpVersion)


if "__main__" == __name__:
    mian()