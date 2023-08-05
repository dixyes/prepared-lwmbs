#!/usr/bin/env php
<?php

// fetch aarch64 glibc from centos-altarch
// TODO: support other archs

$mirror = getenv('CENTOS_ALTARCH_MIRROR') ?: 'http://mirror.centos.org/altarch/';
@mkdir('/usr/aarch64-linux-gnu/sys-root', recursive: true);
exec("curl -sL \"$mirror\"7/os/aarch64/Packages/", $page, $ret);
$page = implode("\n", $page);
if ($ret != 0) {
    exit("failed fetch page");
}

function getlast($package, $page) {
    preg_match_all('/href="(?<filename>'.$package.'-(?<version>[\d\-.]+)\.el7\.aarch64\.rpm)"/i', $page, $matches);
    if (!$matches) {
        exit("failed finding $package");
    }
    $versions = [];
    foreach($matches['version'] as $i => $version) {
        $versions[str_replace('-', '.', $version)] = $matches['filename'][$i];
    }
    uksort($versions, 'version_compare');
    return end($versions);
}

foreach ([
    'glibc',
    'glibc-common',
    'glibc-devel',
    'glibc-static',
    'glibc-headers',
    'kernel-headers',
] as $package) {
    $file = getlast($package, $page);

    passthru(
        'set -x ; ' .
        "curl -sfL -o /tmp/$file \"$mirror\"7/os/aarch64/Packages/$file && ".
        "cd /usr/aarch64-linux-gnu/sys-root && ".
        "rpm2cpio /tmp/$file | cpio -idmv",
    $ret);
    if ($ret != 0) {
        exit("failed fetch $file");
    }
}