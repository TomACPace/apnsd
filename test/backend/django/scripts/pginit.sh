#!/bin/sh

PGUSER=postgres
DBNAME=apnstest

sudo -u $PGUSER dropdb $DBNAME
sudo -u $PGUSER createdb $DBNAME
sudo -u $PGUSER dropuser $DBNAME
sudo -u $PGUSER createuser $DBNAME -s
python2.5 manage.py syncdb

