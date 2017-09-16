#!/bin/bash

localdir=$1
s3dir=$2

aws s3 sync "$localdir" "$s3dir" \
    --acl public-read

