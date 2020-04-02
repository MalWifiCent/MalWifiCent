#!/bin/bash
#####################################################
# update packege list and upgrade packeges
#####################################################
apt update 
apt upgrade -y

#####################################################
# functions
#####################################################
install_program(){
#for easy install programs:
#check if program is installed and if not, install it
dpkg -s $1 &>/dev/null
	if [ $? != 0 ] #if program is not installed
		then 
			echo install $1
			apt install $1 -y
			echo $1 installed
	else echo $1 is already installed
fi
}


#####################################################
# easy install programs
#####################################################
install_program gcc
install_program tcpdump
install_program wireshark
install_program open-vm-tools-desktop
install_program python3-pip


#####################################################
# custom install programs
#####################################################

#INetSim

dpkg -s inetsim &>/dev/null
if [[ $? != 0 ]]
	then 
		echo installing inetsim
		echo "deb http://www.inetsim.org/debian/ binary/" > /etc/apt/sources.list.d/inetsim.list
		echo "deb-src http://www.inetsim.org/debian/ source/" >> /etc/apt/sources.list.d/inetsim.list
		wget -O - https://www.inetsim.org/inetsim-archive-signing-key.asc | apt-key add -
		apt install inetsim -y
		systemctl disable inetsim  # Don't automatically run INetSim on startup
		echo inetsim is installed
	else
		echo inetsim is already installed
fi

#####################################################
# pip install from requirements.txt
#####################################################
pip3 install -r ../requirements.txt

#####################################################
#find path to script
#####################################################
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
#####################################################
# Create Malwificent service file (etc/systmd/system)
#####################################################
USERNAME=$(logname)
cat > /etc/systemd/system/MalWiFiCent.service <<EOF
# This service executes the MalWiFiCent_startup script on every host boot up

[Unit]
Description=MalWiFiCent service
After=network.target

[Service]
ExecStart=sudo python3 /home/$USERNAME/Documents/MalWiFicent/src/server.py

[Install]
WantedBy=multi-user.target
EOF

chmod +x /etc/init.d/MalWiFiCent_startup.sh

sudo systemctl start MalWiFiCent.service
sudo systemctl enable MalWiFiCent.service
systemctl daemon-reload

python3 $SCRIPTPATH/server.py