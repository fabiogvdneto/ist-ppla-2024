#!/bin/sh
rm ./out/* 2>/dev/null

# Solve instances of the test scheduling problem
# and validate the solution with the checker.py
# provided by the university.
# -----------------------------------------------------
# usage: ./test.sh <path-to-instances or instance-file>
for path in $@; do
    for file in `find $path -maxdepth 1 -type f | sort -V`; do
        echo --------------
        echo Optimizing ${file}...
        python ./proj.py $file ./out/`basename $file`
        python ./checker.py $file ./out/`basename $file`
    done
done