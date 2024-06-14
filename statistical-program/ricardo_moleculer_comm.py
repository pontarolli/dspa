# source myenv/bin/activate

import pandas as pd
import matplotlib.pyplot as plt
import os   # for file management


################## GLOBAL VARIABLE
#file name
filename = '2024-07-06-14h54.txt'
filename_mod = filename+'_mod.txt'
excel_file = filename+'.xlsx'
pcpac_file = '2024-07-06-14h54.pcap'

#device mac address
gw_mac='00:00:00:00:00:00'
plc_mac='00:00:00:00:00:00'




################## READ DATA from NodeRed
print("Lettura file, ", filename)

column_name_timestamp=['t0','t1','t2','t3','t4','t5','t6','t7']
column_name_data=['L01','L12','L23','L34','L45','L56','L67','L04','L47']

#read and modify file
with open(filename, 'r') as f:
    data = f.read().replace('[', '').replace(']','')
    
with open(filename_mod, 'w') as f:
    f.write(data)

timestamp = pd.read_csv(filename_mod, lineterminator=' ', names=column_name_timestamp)
#convert to int
#timestamp = timestamp.astype(int)

print(timestamp)

################## READ DATA from Sniffer
#to do

################## ELABORATE DATA

print("Elaborazione dati")

latency = pd.DataFrame(columns=column_name_data)

latency['L01'] = timestamp['t1'] - timestamp['t0']
latency['L12'] = timestamp['t2'] - timestamp['t1']
latency['L23'] = timestamp['t3'] - timestamp['t2']
latency['L34'] = timestamp['t4'] - timestamp['t3']
latency['L45'] = timestamp['t5'] - timestamp['t4']
latency['L56'] = timestamp['t6'] - timestamp['t5']
latency['L67'] = timestamp['t7'] - timestamp['t6']
latency['L04'] = timestamp['t4'] - timestamp['t0']
latency['L47'] = timestamp['t7'] - timestamp['t4']


print(latency)
print(latency.describe())

################################################ DATA TO EXCEL 

print("Fine elaborazione, salvataggio dati su EXCEL")


latency_stats=latency.describe()

with pd.ExcelWriter(excel_file) as writer: 
    timestamp.to_excel(writer, sheet_name='row timestamp')
    latency.to_excel(writer, sheet_name='latency')
    latency_stats.to_excel(writer, sheet_name='statistics')

################ PLOT DATA

print("Plotting ... CNTRL+C to stop")

#plot parameters
plt.rcParams.update({'font.size': 12})
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
transparency=0.8
marker_size=10
number_of_bins=10


#plot latency

#SUBPLOT
fig, subplot = plt.subplots(5, 2,figsize=(7,10), layout="constrained")
for i in range(5):
    for j in range(2):
        if i*2+j < len(column_name_data):
            subplot[i,j].plot(latency[column_name_data[i*2+j]], label=column_name_data[i*2+j], marker='o', markersize=marker_size, alpha=transparency)
            subplot[i,j].set_title(column_name_data[i*2+j])
            subplot[i,j].set_xlabel('sample')
            subplot[i,j].set_ylabel('latency (ms)')

#HISTOGRAM
fig, subplot = plt.subplots(5, 2,figsize=(7,10), layout="constrained")
for i in range(5):
    for j in range(2):
        if i*2+j < len(column_name_data):
            subplot[i,j].hist(latency[column_name_data[i*2+j]], bins=number_of_bins, alpha=transparency)
            subplot[i,j].set_title(column_name_data[i*2+j])
            subplot[i,j].set_xlabel('latency (ms)')
            subplot[i,j].set_ylabel('frequency')

#BOXPLOT
fig, subplot = plt.subplots(5, 2,figsize=(7,10), layout="constrained")
for i in range(5):
    for j in range(2):
        if i*2+j < len(column_name_data):
            subplot[i,j].boxplot(latency[column_name_data[i*2+j]])
            subplot[i,j].set_title(column_name_data[i*2+j])
            subplot[i,j].set_ylabel('latency (ms)')

plt.show()

