# prepared-lwmbs

一些准备好可以进行lwmbs构建的环境

dockerhub： https://hub.docker.com/r/dixyes/prepared-lwmbs

## tags

```plain
不带源码：
dixyes/prepared-lwmbs:{variant}-{scripts_rev}-{lwmbs_rev}
带源码:
dixyes/prepared-lwmbs:{variant}-src-{src_hash}
```

| variant | 说明 |
| - | - |
| linux-glibc-x86_64 | 基于centos:7的x86_64本机构建镜像 |
| linux-glibc-aarch64 | 基于fedora，使用centos-altarch的glibc的arm64本机构建镜像 |

scripts_rev: 这个仓库的提交号
lwmbs_rev: lwmbs提交号
src_hash: 源码hash
