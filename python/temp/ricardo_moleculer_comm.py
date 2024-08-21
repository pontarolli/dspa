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




# ################## GLOBAL VARIABLE
# #file name
# filename = '/home/usr/dspa/experiments/2024-07-31/2024-07-31-10-08-real.txt'
# filename_mod = filename+'_mod.txt'
# excel_file = filename+'.xlsx'
# pcap_file = '/home/usr/dspa/experiments/2024-07-31/2024-07-31-10-08-real.pcap'

# Base path
base_path = '/home/usr/dspa/experiments/2024-07-31/2024-07-31-09-27-real'

# Constructed file paths
filename = f'{base_path}.txt'
filename_mod = f'{base_path}_mod.txt'
excel_file = f'{base_path}.xlsx'
pcap_file = f'{base_path}.pcap'



#device mac address
gw_mac='00:00:00:00:00:00'
plc_mac='00:00:00:00:00:00'


################## READ DATA from NodeRed
print("Lettura file, ", filename)

column_name_timestamp=['t1','t3','t5','t6','t7','t8','t9','t11']
columns_sniffer=['t2','t4','t10','t12']
# column_name_data=['$L_{1;2}$','$L_{2;3}$','$L_{3;4}$','$L_{4;5}$',
#                   '$L_{5;6}$','$L_{6;7}$','$L_{7;8}$','$L_{8;9}$',
#                   '$L_{9;10}$','$L_{10;11}$','$L_{11;12}$','$L_{1;3}$',
#                   '$L_{3;5}$','$L_{9;11}$','$L_{1;7}$','$L_{7;11}$']

column_name_data=['$L_{1;2}$','$L_{2;4}$','$L_{4;5}$',
                  '$L_{5;6}$','$L_{6;7}$','$L_{7;8}$','$L_{8;9}$',
                  '$L_{9;10}$','$L_{10;12}$',
                  '$L_{1;7}$']

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

latency[column_name_data[0]] = timestamp['t2']-timestamp['t1'] # At21    (1)
                                                               # min     (2) 
latency[column_name_data[1]] = timestamp['t4']-timestamp['t2'] 
                                        # t4  -(t2 + min (2))            (3)
latency[column_name_data[2]] = timestamp['t5']-timestamp['t4']
latency[column_name_data[3]] = timestamp['t6']-timestamp['t5']
latency[column_name_data[4]] = timestamp['t7']-timestamp['t6']
latency[column_name_data[5]] = timestamp['t8']-timestamp['t7']
latency[column_name_data[6]] = timestamp['t9']-timestamp['t8']
latency[column_name_data[7]] = timestamp['t10']-timestamp['t9'] # At109  (4)
                                                                # min    (5)
latency[column_name_data[8]] = timestamp['t12']-timestamp['t10']
                                        # t12 -(t10 + min(5))            (6)
latency[column_name_data[9]] = timestamp['t7']-timestamp['t1']


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
plt.rcParams.update({'font.size': 10})
#plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["font.family"] = "Times New Roman"
transparency=0.8
marker_size=5
number_of_bins=10


#plot latency

#change figure size
column=4
row=4
cont=0
#SUBPLOT
fig, subplot = plt.subplots(row, column,figsize=(14,10), layout="constrained")
for i in range(row):
    for j in range(column):
        if cont < len(column_name_data):
            subplot[i,j].plot(latency[column_name_data[cont]], label=column_name_data[cont], marker='o', markersize=marker_size, alpha=transparency)
            subplot[i,j].set_title(column_name_data[cont])
            subplot[i,j].set_xlabel(' ')
            subplot[i,j].set_ylabel(' ')
        cont=cont+1 
        
fig.text(0.5, 0.01, 'Samples', ha='center', fontsize=12)
fig.text(0.01, 0.5, 'Latency (ms)', va='center', rotation='vertical', fontsize=12)

#HISTOGRAM
cont=0
fig, subplot = plt.subplots(row, column,figsize=(14,10), layout="constrained")
for i in range(row):
    for j in range(column):
        if cont < len(column_name_data):
            subplot[i,j].hist(latency[column_name_data[cont]], bins=number_of_bins, alpha=transparency)
            subplot[i,j].set_title(column_name_data[cont])
            subplot[i,j].set_xlabel(' ')
            subplot[i,j].set_ylabel(' ')
        cont=cont+1
fig.text(0.5, 0.01, 'Latency (ms)', ha='center', fontsize=12)
fig.text(0.01, 0.5, 'Frequency', va='center', rotation='vertical', fontsize=12)

#BOXPLOT
cont=0
fig, subplot = plt.subplots(row, column,figsize=(14,10), layout="constrained")
for i in range(row):
    for j in range(column):
        if cont < len(column_name_data):
            subplot[i,j].boxplot(latency[column_name_data[cont]])
            subplot[i,j].set_xticklabels([column_name_data[cont]])
            #subplot[i,j].set_xlabel(column_name_data[cont])
            subplot[i,j].set_ylabel(' ')
        cont=cont+1

fig.text(0.01, 0.5, 'Latency (ms)', va='center', rotation='vertical', fontsize=12)
fig.text(0.5, 0.01, 'Experiments', va='center', fontsize=12)
plt.show()
