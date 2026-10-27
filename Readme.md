# prepared-lwmbs

一些准备好可以进行lwmbs构建的环境

https://ghcr.io/dixyes/prepared-lwmbs

## tags

```plain
不带源码：
ghcr.io/dixyes/prepared-lwmbs:{variant}-{base_date}-{lwmbs_rev}
```

每个variant另外维护一个moving tag `{variant}`，指向最近一次构建。

| variant | 基础镜像 | 说明 |
| - | - | - |
| linux-glibc-x86_64 | quay.io/pypa/manylinux2014_x86_64 | x86_64本机构建，gcc 11（devtoolset-11） |
| linux-glibc-aarch64 | quay.io/pypa/manylinux2014_aarch64 | aarch64本机构建，gcc 10（该架构无devtoolset-11） |
| linux-musl-x86_64 | quay.io/pypa/musllinux_1_2_x86_64 | x86_64本机构建，gcc由基础镜像提供 |
| linux-musl-aarch64 | quay.io/pypa/musllinux_1_2_aarch64 | aarch64本机构建，gcc由基础镜像提供 |

base_date: 基础镜像tag的日期，当前为2026.10.25

lwmbs_rev: lwmbs提交号

镜像内还包含PHP CLI 8.5.12（/opt/php）、re2c、cmake、node与lwmbs克隆（/lwmbs）。
