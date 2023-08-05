#!/usr/bin/env bash

if [ -n "$CI" ]
then
    CENTOS_MIRROR=https://mirror.facebook.net/centos/
    EPEL_MIRROR=https://mirror.facebook.net/fedora/epel/
    SCLO_MIRROR=https://mirror.facebook.net/centos/7/sclo/
    GNU_MIRROR=https://mirrors.ustc.edu.cn/gnu/
else
    CENTOS_MIRROR=https://mirror.ustc.edu.cn/centos/
    EPEL_MIRROR=https://mirrors.ustc.edu.cn/epel/
    SCLO_MIRROR=https://mirrors.ustc.edu.cn/centos/7/sclo/
    GNU_MIRROR=https://mirrors.ustc.edu.cn/gnu/
fi

# Build for linux-glibc-x86_64

docker build . -f Dockerfile.linux-glibc-x86_64 -t dixyes/prepared-lwmbs:linux-glibc-x86_64 \
    --build-arg "CENTOS_MIRROR=${CENTOS_MIRROR}" \
    --build-arg "EPEL_MIRROR=${EPEL_MIRROR}" \
    --build-arg "SCLO_MIRROR=${SCLO_MIRROR}" \
    --build-arg "GNU_MIRROR=${GNU_MIRROR}"

scripts_rev="$(git rev-parse HEAD)"
lwmbs_rev="$(docker run --rm dixyes/prepared-lwmbs:linux-glibc-x86_64 sh -c 'cd /lwmbs && git rev-parse HEAD')"
docker tag dixyes/prepared-lwmbs:linux-glibc-x86_64 "dixyes/prepared-lwmbs:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev}"

docker push dixyes/prepared-lwmbs:linux-glibc-x86_64
docker push "dixyes/prepared-lwmbs:linux-glibc-x86_64-${scripts_rev}-${lwmbs_rev}"
