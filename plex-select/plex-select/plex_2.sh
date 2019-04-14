# Miniconda3
aws s3 cp s3://manny-and-meche-plex/Miniconda3-latest-Linux-x86_64.sh Miniconda3-latest-Linux-x86_64.sh --region us-east-1
bash Miniconda3-latest-Linux-x86_64.sh -b -p /home/ubuntu/miniconda3
export PATH=/home/ubuntu//miniconda3/bin:$PATH
conda install selenium -y

# Google Chrome
aws s3 cp s3://manny-and-meche-plex/google-chrome-stable_current_amd64.deb google-chrome-stable_current_amd64.deb --region us-east-1
apt-get install -y libappindicator1 fonts-liberation
dpkg --configure -a
dpkg -i google-chrome*.deb
apt-get -f install -y
dpkg -i google-chrome*.deb

# Plex Media Server
aws s3 cp s3://manny-and-meche-plex/plexmediaserver_1.13.9.5439-7303bc002_amd64.deb plexmediaserver_1.13.9.5439-7303bc002_amd64.deb --region us-east-1
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
aws s3 cp "s3://manny-and-meche-plex/Movies/$1.*" "$1.*"

# Python File
cd /home/ubuntu/
aws s3 cp s3://manny-and-meche-plex/plex_setup.py plex_setup.py --region us-east-1
python plex_setup.py
