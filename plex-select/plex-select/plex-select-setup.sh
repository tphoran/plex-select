#!/bin/bash

# Get EC2 Info for Movie Name
INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)
aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" --region us-east-1
MOVIE=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" --region us-east-1 | jq '.["Tags"][0]["Value"]' | tr -d '"')
RELAUNCH=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" --region us-east-1 | jq '.["Tags"][2]["Value"]' | tr -d '"')
OWNER=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" --region us-east-1 | jq '.["Tags"][1]["Value"]' | tr -d '"')

# Add Cloud Watch Alarm to Shut Down After Usage
# aws cloudwatch put-metric-alarm --region=us-east-1 --alarm-name $INSTANCE_ID --alarm-description "Terminate when CPU < 1 percent for 3 hours" --metric-name CPUUtilization --namespace AWS/EC2 --statistic Average --period 300 --threshold 1 --comparison-operator LessThanThreshold  --dimensions "Name=InstanceId,Value=$INSTANCE_ID" --evaluation-periods 36 --alarm-actions arn:aws:automate:us-east-1:ec2:terminate --unit Percent
aws cloudwatch put-metric-alarm --region=us-east-1 --alarm-name $INSTANCE_ID --alarm-description "Terminate when Network Packets Out < 100 for 1 hour" --metric-name NetworkPacketsOut --namespace AWS/EC2 --statistic Average --period 300 --threshold 100 --comparison-operator LessThanThreshold  --dimensions "Name=InstanceId,Value=$INSTANCE_ID" --evaluation-periods 12 --alarm-actions arn:aws:automate:us-east-1:ec2:terminate --unit Count

# Miniconda3
cd /home/ubuntu/
aws s3 cp s3://manny-and-meche-plex/Miniconda3-latest-Linux-x86_64.sh Miniconda3-latest-Linux-x86_64.sh --region us-east-1
bash Miniconda3-latest-Linux-x86_64.sh -b -p /home/ubuntu/miniconda3
export PATH=/home/ubuntu//miniconda3/bin:$PATH
conda install selenium -y
conda install sys -y
conda install -c anaconda boto3 -y

# Google Chrome
aws s3 cp s3://manny-and-meche-plex/google-chrome-stable_current_amd64.deb google-chrome-stable_current_amd64.deb --region us-east-1
apt-get install -y libappindicator1 fonts-liberation
dpkg --configure -a
dpkg -i google-chrome*.deb
apt-get -f install -y
dpkg -i google-chrome*.deb

# Plex Media Server
aws s3 cp s3://manny-and-meche-plex/plexmediaserver_1.14.1.5488-cc260c476_amd64.deb plexmediaserver_1.14.1.5488-cc260c476_amd64.deb --region us-east-1
dpkg -i plexmediaserver*.deb
systemctl enable plexmediaserver.service
systemctl start plexmediaserver.service

# Chromedriver
cd /home/ubuntu/miniconda3/bin/
aws s3 cp s3://manny-and-meche-plex/chromedriver chromedriver --region us-east-1
chown root:root chromedriver
chmod +x chromedriver

# Media File
mkdir -p /var/lib/plexmediaserver/Movies
cd /var/lib/plexmediaserver/Movies
aws s3 cp "s3://manny-and-meche-plex/Movies/$MOVIE.m4v" "$MOVIE.m4v"

# Python File
cd /home/ubuntu/
aws s3 cp s3://manny-and-meche-plex/plex-select-setup.py plex-select-setup.py --region us-east-1
python plex-select-setup.py $INSTANCE_ID $OWNER $RELAUNCH $MOVIE
