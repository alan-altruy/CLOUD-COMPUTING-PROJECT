#!/usr/bin/env bash
set -e

wget https://cluster.ig.umons.ac.be/workshop_ia/image.orig.zip -O image.orig.zip
unzip -o image.orig.zip -d static/
rm image.orig.zip