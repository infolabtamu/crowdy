#!/bin/bash
export PYTHONPATH=".."
cd tests
for t in basic file
do
    echo "running $t"
    python $t"_tests.py"
done

echo "running mock"
python database_tests.py mock
python query_tests.py mock

echo "running couch"
python database_tests.py couch

echo "running mongo"
python database_tests.py mongo
python query_tests.py mongo
