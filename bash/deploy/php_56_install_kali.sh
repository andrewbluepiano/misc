# Intended to be used to get Apache2 and PHP v5.6 onto a Kali rolling machine. 
sudo su
apt-get update
apt-get install apache2
rm /etc/apt/sources.list.d/php.list 2>/dev/null && \
apt-get -y install apt-transport-https && \
wget -q https://packages.sury.org/php/apt.gpg -O- | sudo apt-key add - && \
echo 'deb https://packages.sury.org/php/ stretch main'>/etc/apt/sources.list.d/php.list && \
apt-get update && \
apt-get -y install php5.6 php5.6-mbstring php5.6-mcrypt php5.6-mysql php5.6-xml
a2dismod php7.4 && \
sudo a2enmod php5.6 && \
sudo service apache2 restart && \
sudo update-alternatives --set php /usr/bin/php5.6
