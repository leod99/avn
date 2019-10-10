#!/bin/bash

echo "===Copy pub key to remote hosts==="
input="./hostnames.txt"
# please replace avnadmin with existing user on remote host
while IFS= read -r line
do
  echo "$line"
  scp ./hostsecrets/monitoradmin.pub avnadmin@$line:~/.ssh/authorized_keys
done < "$input"

sudo chmod 400 ./hostsecrets/monitoradmin.pem
sudo chmod +x ./runjob.sh

echo "===Install packages==="
# install packages
sudo apt update

sudo apt install curl
sudo apt install python-pip
# or use below for python3
# sudo apt install python3-pip
sudo pip install fabric2
# or use below for python3
#sudo pip3 install fabric2

sudo pip install "confluent-kafka[avro]"
sudo pip install requests
# set up ssh cert

echo "===Setup crontab==="
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $DIR
croncmd="/bin/bash $DIR/runjob.sh >> /var/log/cron.log 2>&1"
cronjob="*/5 * * * * $croncmd"
cat <(fgrep -i -v "$croncmd" <(sudo crontab -l)) <(echo "$cronjob") | sudo crontab -


