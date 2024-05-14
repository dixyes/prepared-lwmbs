# prepared-lwmbs

一些准备好可以进行lwmbs构建的环境

dockerhub： https://hub.docker.com/r/dixyes/prepared-lwmbs

## tags

```plain
不带源码：
dixyes/prepared-lwmbs:{variant}-{lwmbs_rev}
```

| variant | 说明 |
| - | - |
| linux-glibc-x86_64 | 基于centos:7的x86_64本机构建镜像 |
| linux-glibc-aarch64 | 基于fedora，使用centos-altarch的glibc的x86_64host arm64target交叉构建镜像 |
| linux-musl-x86_64 | 基于alpine的x86_64本机构建镜像 |
| linux-musl-aarch64 | 基于alpine，使用musl.cc的gcc的x86_64host arm64targe交叉构建镜像 |

lwmbs_rev: lwmbs提交号
