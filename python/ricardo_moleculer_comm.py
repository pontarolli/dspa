import pandas as pd
import matplotlib.pyplot as plt
import os   # for file management
from binascii import hexlify
from scapy.all import *             #for pcap file
from scapy.utils import *           #for pcap file

################################### DIAGRAM ############################################

#SENSOR          #TRANSPORTER            #NodeRed           #SNIFFER         #PLC        
#                                           T1-------------->T2-------------->T3         
#                                           
#                                           T5<--------------T4<----------------
#                                           
# T6<-----------------------------------------
# ----------------------------------------->T7
# T8<-----------------------------------------
# ----------------------------------------->T9    
#                                           ---------------->T10---------------->T11
#                                           <----------------T12<----------------




################## GLOBAL VARIABLE
#file name
filename = '16-10-18-06-2024.txt'
filename_mod = filename+'_mod.txt'
excel_file = filename+'.xlsx'
pcap_file = '16-10-18-06-2024.pcap'

#device mac address
gw_mac='00:00:00:00:00:00'
plc_mac='00:00:00:00:00:00'


################## READ DATA from NodeRed
print("Lettura file, ", filename)

column_name_timestamp=['t1','t3','t5','t6','t7','t8','t9','t11']
columns_sniffer=['t2','t4','t10','t12']
column_name_data=['L12','L23','L34','L45','L56','L67','L78','L89','L910','L1011','L1112','L13','L35','L911','L17','L711']

#read and modify file
with open(filename, 'r') as f:
    data = f.read().replace('[', '').replace(']','')
    
with open(filename_mod, 'w') as f:
    f.write(data)

timestamp = pd.read_csv(filename_mod, lineterminator=' ', names=column_name_timestamp)

################## READ DATA from Sniffer

print("Elaborazione pacchetti...")
#read pcap file
pcap = rdpcap(pcap_file)

 #define dataframe
columns_sniffer=['t2','t4','t10','t12']
df_sniffer=pd.DataFrame(columns=columns_sniffer)

timestamp_read_request=[]
timestamp_write_request=[]
timestamp_read_response=[]
timestamp_write_response=[]
timestamp_kunbus_read_request=[]
timestamp_kunbus_write_request=[]
timestamp_kunbus_write_response=[]
timestamp_kunbus_read_response=[]


#read pcap and extract data only from s7comm packets
for pkt in pcap:
    
    try:
        if pkt.payload.proto == 6: #indicates TCP, ICMP = 1
            if Raw in pkt: #check if there is raw data
                #get payload
                load=pkt[Raw].load
                loadHEX=hexlify(load)

                #check if is s7comm packet
                if loadHEX[14:16] == b'32': #if true is s7comm packet
                    #get time for each packet
                    tmstamp=float(pkt.time)

                    #check action of the packet (b'04' is read, b'05' is write)
                    if loadHEX[34:36] == b'04':
                        #READ request
                        timestamp_read_request.append(tmstamp)

                        data=loadHEX[len(loadHEX)-16:len(loadHEX)]
                        #divide data in 2 byte
                        data1=data[0:8]
                        data2=data[8:16]
                        #convert data in decimal
                        data1=int(data1,16)
                        data2=int(data2,16)
                        #convert data in float
                        data=data1+data2/1000000000
                        timestamp_kunbus_read_request.append(data)
                    
                    elif loadHEX[38:40] == b'04':
                        #READ ACK
                        timestamp_read_response.append(tmstamp)

                        data=loadHEX[len(loadHEX)-16:len(loadHEX)]
                        #divide data in 2 byte
                        data1=data[0:8]
                        data2=data[8:16]
                        #convert data in decimal
                        data1=int(data1,16)
                        data2=int(data2,16)
                        #convert data in float
                        data=data1+data2/1000000000
                        timestamp_kunbus_read_response.append(data)


                    
                    elif loadHEX[34:36] == b'05':
                        #WRITE request
                        timestamp_write_request.append(tmstamp)
                        data=loadHEX[len(loadHEX)-16:len(loadHEX)]
                        #divide data in 2 byte
                        data1=data[0:8]
                        data2=data[8:16]
                        #convert data in decimal
                        data1=int(data1,16)
                        data2=int(data2,16)
                        #convert data in float
                        data=data1+data2/1000000000
                        timestamp_kunbus_write_request.append(data)
                    
                    elif loadHEX[38:40] == b'05':
                        #WRITE ack
                        timestamp_write_response.append(tmstamp)
                        data=loadHEX[len(loadHEX)-16:len(loadHEX)]
                        #divide data in 2 byte
                        data1=data[0:8]
                        data2=data[8:16]
                        #convert data in decimal
                        data1=int(data1,16)
                        data2=int(data2,16)
                        #convert data in float
                        data=data1+data2/1000000000
                        timestamp_kunbus_write_response.append(data)

    except AttributeError:
        pass

#processing timestamp
timestamp_read_request=[int(x*1000) for x in timestamp_read_request]
timestamp_write_request=[int(x*1000) for x in timestamp_write_request]
timestamp_read_response=[int(x*1000) for x in timestamp_read_response]
timestamp_write_response=[int(x*1000) for x in timestamp_write_response]

timestamp['t2']=timestamp_read_request[0::2]
timestamp['t4']=timestamp_read_response[0::2]
timestamp['t10']=timestamp_write_request
timestamp['t12']=timestamp_write_response

print("Pacchetti elaborati")
print("Pacchetti letti: ", len(timestamp_read_request))
print("Pacchetti letti akc: ", len(timestamp_read_response))
print("Pacchetti scritti: ", len(timestamp_write_request))
print("Pacchetti scritti ack: ", len(timestamp_write_response))

print("Pacchetti Kunbus letti: ", len(timestamp_kunbus_read_request))
print("paccetti Kunbus letti ack: ", len(timestamp_kunbus_read_response))
print("Pacchetti Kunbus scritti: ", len(timestamp_kunbus_write_request))
print("Pacchetti Kunbus scritti ack: ", len(timestamp_kunbus_write_response))


################## ELABORATE DATA

print("Elaborazione dati")

latency = pd.DataFrame(columns=column_name_data)

latency['L12'] = timestamp['t2']-timestamp['t1']
latency['L23'] = timestamp['t3']-timestamp['t2']
latency['L34'] = timestamp['t4']-timestamp['t3']
latency['L45'] = timestamp['t5']-timestamp['t4']
latency['L56'] = timestamp['t6']-timestamp['t5']
latency['L67'] = timestamp['t7']-timestamp['t6']
latency['L78'] = timestamp['t8']-timestamp['t7']
latency['L89'] = timestamp['t9']-timestamp['t8']
latency['L910'] = timestamp['t10']-timestamp['t9']
latency['L1011'] = timestamp['t11']-timestamp['t10']
latency['L1112'] = timestamp['t12']-timestamp['t11']
latency['L13'] = timestamp['t3']-timestamp['t1']
latency['L35'] = timestamp['t5']-timestamp['t3']
latency['L911'] = timestamp['t11']-timestamp['t9']
latency['L17'] = timestamp['t7']-timestamp['t1']
latency['L711'] = timestamp['t11']-timestamp['t7']


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

#change figure size


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
