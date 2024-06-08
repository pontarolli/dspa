import pandas as pd
import matplotlib.pyplot as plt
import os   # for file management


################## GLOBAL VARIABLE
filename = 'data.txt'
filename_mod = 'data_mod.txt'


################## READ DATA from NodeRed
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

#print how many L67 are less than 0
count=0
for l in latency['L67']:
    if l<0:
        count+=1

print(count)