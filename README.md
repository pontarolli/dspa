# Doctoral Sandwich Program Abroad (DSPA) 
Description

## Overview
![Diagrama](diagram/diagram.drawio.svg)

## PLC Siemens
Program

## Moleculer Services
Services

## Composer Node-RED
Flows

## Statistical
The [python program](./python/ricardo_moleculer_comm.py) calculates the △T (ms) between the raw timestamps (UTC) at [experiments](./experiments/)  collected in Node-Red, Industrial PC and Sniffer, all sync with NTP device, where at the end generates a histogram and boxplot.

```bash
# install python
sudo apt install python3
# install package manager
sudo apt install python3-pip
# install virtual environment creator to install packages
sudo apt install python3-venv

# Create a project folder
mkdir python
# Create the main code
nano ricardo_moleculer_comm.py
# Create a virtual environment
python3 -m venv myenv
# Activate the virtual environment 
source myenv/bin/activate
# Install the packages
pip install pandas
# Generate the requirements.txt
pip freeze > requirements.txt
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the Code and then save the images manually.
python ricardo_moleculer_comm.py

# Disable the virtual environment
deactivate
```

## Conclusion
Article

## Authors
Ricardo  
Massimiliano  
Paolo  
Eduardo  





