#!/bin/bash

mysql -D CRSdb -e "DELETE FROM \`$1\` WHERE \`$2\` < now()-interval $3;"
