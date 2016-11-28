#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:./lib/tracknodes"
coverage run --source=tracknodes $(which nosetests) -w test/units/
