#!/usr/bin/env bash

if [ -n "$CI" ]
then
    CENTOS_MIRROR=https://mirror.facebook.net/centos/
    EPEL_MIRROR=https://mirror.facebook.net/fedora/epel/
    SCLO_MIRROR=https://mirror.facebook.net/centos/7/sclo/
    GNU_MIRROR=https://mirror.facebook.net/gnu/
    FEDORA_MIRROR=https://mirror.facebook.net/fedora/linux/
    CENTOS_ALTARCH_MIRROR=https://mirror.facebook.net/centos-altarch/
else
    CENTOS_MIRROR=https://mirrors.ustc.edu.cn/centos/
    EPEL_MIRROR=https://mirrors.ustc.edu.cn/epel/
    SCLO_MIRROR=https://mirrors.ustc.edu.cn/centos/7/sclo/
    GNU_MIRROR=https://mirrors.ustc.edu.cn/gnu/
    FEDORA_MIRROR=https://mirrors.ustc.edu.cn/fedora/
    CENTOS_ALTARCH_MIRROR=https://mirrors.ustc.edu.cn/centos-altarch/
fi

LWMBS_REPO="${LWMBS_REPO-https://github.com/dixyes/lwmbs}"
LWMBS_BRANCH="${LWMBS_BRANCH-master}"
IMAGE_NAME="${IMAGE_NAME-dixyes/prepared-lwmbs}"

scripts_rev="$(git rev-parse HEAD)"
lwmbs_rev="$(git ls-remote "$LWMBS_REPO" "$LWMBS_BRANCH" | awk '{print $1}')"

docker pull . -f Dockerfile.linux-glibc-x86_64 -t "${IMAGE_NAME}:linux-glibc-x86_64"
src_hash="$(docker run --rm "${IMAGE_NAME}:linux-glibc-x86_64" php /lwmbs/fetch_source.php --hash "" "")"

build()
{
    local type="$1"
    
}

# Build for linux-glibc-x86_64

if ! docker manifest inspect "${IMAGE_NAME}:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev}" &> /dev/null
then
    docker buildx build . -f Dockerfile.linux-glibc-x86_64 -t "${IMAGE_NAME}:linux-glibc-x86_64" \
        --build-arg "CENTOS_MIRROR=${CENTOS_MIRROR}" \
        --build-arg "EPEL_MIRROR=${EPEL_MIRROR}" \
        --build-arg "SCLO_MIRROR=${SCLO_MIRROR}" \
        --build-arg "GNU_MIRROR=${GNU_MIRROR}"

    docker tag "${IMAGE_NAME}:linux-glibc-x86_64" "${IMAGE_NAME}:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev}"

    docker push "${IMAGE_NAME}:linux-glibc-x86_64"
    docker push "${IMAGE_NAME}:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev}"

    build_src=1
else
    echo "${IMAGE_NAME}:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev} already exists"
fi

if [ -n "$build_src" ] || ! docker manifest inspect "${IMAGE_NAME}:linux-glibc-x86_64-src-${src_hash}" &> /dev/null
then
    docker buildx build . -f Dockerfile.src -t "${IMAGE_NAME}:linux-glibc-x86_64-src-${src_hash}" \
        --build-arg "BASE_TAG=linux-glibc-x86_64"
fi
build_src=

# Build for linux-glibc-aarch64

if ! docker manifest inspect "${IMAGE_NAME}:linux-glibc-aarch64-${scripts_rev}-${lwmbs_rev}" &> /dev/null
then
    docker buildx build . -f Dockerfile.linux-glibc-aarch64 -t ${IMAGE_NAME}:linux-glibc-aarch64 \
        --build-arg "FEDORA_MIRROR=${FEDORA_MIRROR}" \
        --build-arg "CENTOS_ALTARCH_MIRROR=${CENTOS_ALTARCH_MIRROR}"

    docker tag "${IMAGE_NAME}:linux-glibc-aarch64" "${IMAGE_NAME}:linux-glibc-aarch64-${scripts_rev}-${lwmbs_rev}"

    docker push "${IMAGE_NAME}:linux-glibc-aarch64"
    docker push "${IMAGE_NAME}:linux-glibc-aarch64-${scripts_rev}-${lwmbs_rev}"
else
    echo "${IMAGE_NAME}:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev} already exists"
fi
