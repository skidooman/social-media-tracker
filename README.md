# social-media-tracker
To install postgresql in Ubuntu 20.04, do:

sudo apt install postgresql postgresql-contrib

To launch the server

sudo systemctl start postgresql.service
sudo pg_ctlcluster 12 main start

Then create a database

sudo -i -u postgres
psql
CREATE DATABASE tracker;

exit
exit


TO LIST INTERNALS OF DATABASE IN PSQL

\c tracker
\dt
