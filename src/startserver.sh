#!/bin/bash
export FLASK_APP=agentportal.py
# Make sure our working directory is the directory of this script
cd "${0%/*}"
# IMPORTANT: in a production app we would deploy this with a WSGI container or 
# other option. Flask's server is not meant for production, obviously.
python -m flask run --host=0.0.0.0