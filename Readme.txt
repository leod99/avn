
0. Please skip this, ssh pem/pub file are generated in hostsecrets/
https://askubuntu.com/questions/644020/how-to-generate-openssl-pem-file-and-where-we-have-to-place-it

$ssh-keygen -t rsa -b 2048 -v
mv monitoradmin monitoradmin.pem


1. Please skip if git/python is installed on Linux host already
Install git on Debian / Ubuntu
$ sudo apt-get update
$ sudo apt-get install git

Install git on CentOS/RedHat Linux
sudo yum update
sudo yum install git

Install python
https://docs.python-guide.org/starting/install3/linux/


2. 
Create kafka service from Aiven web UI,
enable config kafka.auto_create_topics_enable
enable REST API, KAfka connect,  Schema Registry

Download ca.pem  service.cert  service.key for kafka server

Create postgres service on web


3. Pull git repo from https://github.com/leod99/avn
run
$git clone https://github.com/leod99/avn
then
$chmod +x *.sh


4. Download ca.pem  service.cert  service.key for kafka server on Aiven web UI to folder secrets/

change user/password/user.info/url accordingly in file(can be found on Aiven web UI)
json/sink_config.json

set KAFKA_SERVER, SCHEMA_REGISTRY_URL, USER in fabrun.py
set SCHEMA_REGISTRY_URL, KAFKA_CONNECT_URL in register_schema.py


5. Set up remote & local env
add hostnames to be monitored in hostnames.txt
replace username "avnadmin" in aptsetup.sh/yumsetup.sh with existing user on remote hosts

for Debian / Ubuntu local host
run $./aptsetup.sh

for CentOS/RedHat Linux local host
run $./yumsetup.sh

Set up Kafka schema and connector
run 
$python register_schema.py


6. verify crontab is set up with
$sudo crontab -e

verify Kafka schema and connector on web UI
(note: connector add runs intermittently successful, 
restart Kafka service and retry if any error occurs)


7. Metric message generation runs every 5mins, or can be invoked manually by
$./runjob.sh
or
$python fabrun.py

verify on Postgres server,
$sudo apt install postgresql postgresql-contrib
$sudo -i -u postgres

$psql -h pg-1cabf9bc-chrdeng9-e577.aivencloud.com -p 16118 -U avnadmin -d defaultdb

=>\dt
=>select * from metrics;
 disk | memory |                         host                          | cpu |      timestamp      | desc 
------+--------+-------------------------------------------------------+-----+---------------------+------
   16 |    0.9 | ec2-52-63-51-102.ap-southeast-2.compute.amazonaws.com |   0 | 2019-10-09 23:27:42 | 
   16 |    0.9 | ec2-52-63-51-102.ap-southeast-2.compute.amazonaws.com |   0 | 2019-10-09 23:33:27 | 
   16 |    0.9 | ec2-52-63-51-102.ap-southeast-2.compute.amazonaws.com | 3.2 | 2019-10-09 23:40:34 | 
   16 |    0.9 | ec2-52-63-51-102.ap-southeast-2.compute.amazonaws.com | 3.1 | 2019-10-10 00:23:20 | 


8. TODO.
add more metrics/automation,
adjust code comment/format, centralize config file for env variables, etc.
