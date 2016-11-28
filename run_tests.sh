#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:./lib/"
coverage run --source=tracknodes $(which nosetests) -w test/units/
