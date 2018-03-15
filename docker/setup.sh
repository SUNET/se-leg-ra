#!/bin/sh

set -e
set -x

adduser --system --group se-leg

virtualenv -p python3 /ra/env
cd /ra/src
/ra/env/bin/pip install -U pip
/ra/env/bin/pip install -r requirements.txt
/ra/env/bin/pip install gunicorn

