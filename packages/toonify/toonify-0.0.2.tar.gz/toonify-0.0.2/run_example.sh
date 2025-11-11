#!/bin/bash
# Helper script to run examples with proper PYTHONPATH
export PYTHONPATH=/Users/marcovinciguerra/Desktop/toon:$PYTHONPATH
.venv/bin/python "$@"
