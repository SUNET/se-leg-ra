#!/bin/sh

set -e
set -x

. /ra/env/bin/activate

# These could be set from Puppet if multiple instances are deployed
app_name=${app_name-'se_leg_ra'}
base_dir=${base_dir-'/ra'}
project_dir=${project_dir-"${base_dir}/src"}
app_dir=${app_dir-"${project_dir}/${app_name}"}
cfg_dir=${cfg_dir-"${base_dir}/etc"}
cfg_file=${cfg_file-"${cfg_dir}/app_config.py"}
# These *can* be set from Puppet, but are less expected to...
workers=${workers-1}
worker_class=${worker_class-sync}
worker_threads=${worker_threads-1}
worker_timeout=${worker_timeout-30}

# set PYTHONPATH if it is not already set using Docker environment
export PYTHONPATH=${PYTHONPATH-${project_dir}}
echo "PYTHONPATH=${PYTHONPATH}"

# nice to have in docker run output, to check what
# version of something is actually running.
/ra/env/bin/pip freeze

# Copy static files for data volume use
mkdir -p /ra/static
cp -r /ra/src/se_leg_ra/static/* /ra/static/.

extra_args=""
if [ -d "/opt/se-leg/se-leg-ra/se_leg_ra/" ]; then
    # developer mode, restart on code changes
    extra_args="--reload"
    # Copy static files for data volume use
    cp -r /opt/se-leg/se-leg-ra/se_leg_ra/static/* /ra/static/.
fi

echo ""
echo "$0: Starting ${app_name}"
echo $SE_LEG_RA_SETTINGS
export SE_LEG_RA_SETTINGS=${SE_LEG_RA_SETTINGS-${cfg_file}}
echo $SE_LEG_RA_SETTINGS

exec start-stop-daemon --start -c seleg:seleg --exec \
     /ra/env/bin/gunicorn \
     --pidfile "/var/run/${app_name}.pid" \
     --user=seleg --group=seleg -- \
     --bind 0.0.0.0:5000 \
     --chdir "/tmp" \
     --workers ${workers} --worker-class ${worker_class} \
     --threads ${worker_threads} --timeout ${worker_timeout} \
     --capture-output \
     ${extra_args} se_leg_ra.run:app

