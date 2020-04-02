# MalWiFicent  
MalWiFiCent was founded by three students at Noroff University College as a project. MalWiFiCent is a system that produces a convincing impersonation of internet connectivity, also known as a fake net. It builds on existing tools for fake connectivity, put together in a system that allows the user to customize the fake net in a predefined environment. 

## Install  
1. Clone the MalWiFiCent project to your computer:  
`git clone https://github.com/MalWifiCent/MalWifiCent.git`

2. Navigate to the `src` folder within the project (<git clone dir>/MalWiFiCent/src/).

3. Ensure that apps_install.sh has execution permissions by running the following command:  
`chmod +x apps_install.sh`

4. The MalWifiCent web server should start automatically after installation. To access MalWiFiCent open a web browser and go to 127.0.0.1:5000

**NOTE:**  If the MalWiFiCent web server does not automatically start after the installation is complete (no service running on 127.0.0.1:5000), either reboot the OS or run the following command:  

`sudo python3 src/server.py`

## Running  
`sudo python3 src/server.py`

## Configuration  
Basic settings for the website can be configured inside `src/__init__.py`