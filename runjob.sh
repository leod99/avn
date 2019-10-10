#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo -i -u ldeng -H sh -c "python $DIR/fabrun.py"
