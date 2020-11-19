import sys
import re
import pandas as pd
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import csv


def main ():
    csvORlogs = sys.argv[1]
    
    if csvORlogs == 'logs':
        lightFile = Path(__file__).parent / sys.argv[2]
        tekuFile =  Path(__file__).parent / sys.argv[3]
        nimbusFile = Path(__file__).parent / sys.argv[4]
        prysmFile = Path(__file__).parent / sys.argv[5]
        lodestarFile = Path(__file__).parent / sys.argv[6]
        lightSyncFile = Path(__file__).parent / sys.argv[7]
        tekuSyncFile = Path(__file__).parent / sys.argv[8]
        nimbusSyncFile = Path(__file__).parent / sys.argv[9]
        prysmSyncFile = Path(__file__).parent / sys.argv[10]
        lodestarSyncFile = Path(__file__).parent / sys.argv[11]
        
        
        # Generate panda from lighthouse and create csv file
        lightPanda = getMetricsFromFile('lighthouse',lightFile)
        print("Lighthouse -> PandaObject : Done")
        
        # Generate panda from teku and create csv file
        tekuPanda  = getMetricsFromFile('teku',tekuFile)
        print("Teku -> PandaObject : Done")
        
        # Generate panda from nimbus and create csv file
        nimbusPanda = getMetricsFromFile('nimbus', nimbusFile)
        print("Nimbus -> PandaObject : Done")
        
        # Generate panda from prysm and create csv file
        prysmPanda = getMetricsFromFile('prysm', prysmFile)
        print("Prysm -> PandaObject : Done")
        
        # Generate panda from lodestar and create csv file
        lodestarPanda = getMetricsFromFile('lodestar', lodestarFile)
        print("Lodestar -> PandaObject : Done")
        
        
        # Read the CSV from the 5 clients and parse the data into a panda
        lightSyncPanda = pd.read_csv(lightSyncFile)
        tekuSyncPanda = pd.read_csv(tekuSyncFile)
        nimbusSyncPanda = pd.read_csv(nimbusSyncFile)
        prysmSyncPanda = pd.read_csv(prysmSyncFile)
        lodestarSyncPanda = pd.read_csv(lodestarSyncFile)
        
        # Get peers and slots on the metrics pandas
        addPeersSlotsToPanda(lightPanda, lightSyncPanda, 'TIME', 'Time (hours)', 'Current Slot', 'Peers Connected')
        lightP = Path(__file__).parent / '../../data/Lighthouse/lighthouseMetrics.csv' 
        lightPanda.to_csv(lightP)
        print("Created lighthouseMetrics.csv in data/Lighthouse")
        
        addPeersSlotsToPanda(tekuPanda, tekuSyncPanda, 'TIME', 'Time (hours)', 'Current Slot', 'Peers Connected')
        tekuP = Path(__file__).parent / '../../data/Teku/tekuMetrics3.csv' 
        tekuPanda.to_csv(tekuP)
        print("Created tekuMetrics.csv in data/Teku")
        
        addPeersSlotsToPanda(nimbusPanda, nimbusSyncPanda, 'TIME', 'Time (hours)', 'Current Slot', 'Peers Connected')
        nimbusP = Path(__file__).parent / '../../data/Nimbus/nimbusMetrics.csv'
        nimbusPanda.to_csv(nimbusP)
        print("Created nimbusMetrics.csv in data/Nimbus")
        
        addPeersSlotsToPanda(prysmPanda, prysmSyncPanda, 'TIME', 'Time (hours)', 'Current Slot', 'Peers Connected')
        prysmP = Path(__file__).parent / '../../data/Prysm/prysmMetrics.csv'
        prysmPanda.to_csv(prysmP)
        print("Created prysmMetrics.csv in data/Prysm")
        
        addPeersSlotsToPanda(lodestarPanda, lodestarSyncPanda, 'TIME', 'Time (hours)', 'Current Slot', 'Peers Connected')
        lodestarP = Path(__file__).parent / '../../data/Lodestar/lodestarMetrics.csv'
        lodestarPanda.to_csv(lodestarP)
        print("Created lodestarMetrics.csv in data/Lodestar")
    
        
    elif csvORlogs == 'csv':
        lightFile = Path(__file__).parent / sys.argv[2]
        tekuFile =  Path(__file__).parent / sys.argv[3]
        nimbusFile = Path(__file__).parent / sys.argv[4]
        prysmFile = Path(__file__).parent / sys.argv[5]
        lodestarFile = Path(__file__).parent / sys.argv[6]
        
        lightPanda = pd.read_csv(lightFile)
        tekuPanda = pd.read_csv(tekuFile)
        nimbusPanda = pd.read_csv(nimbusFile)
        prysmPanda = pd.read_csv(prysmFile)
        lodestarPanda = pd.read_csv(lodestarFile)
        
    elif csvORlogs == 'teku':
        teku1File = Path(__file__).parent / sys.argv[2]
        teku2File = Path(__file__).parent / sys.argv[3]
        
        teku1Panda = pd.read_csv(teku1File) 
        print(sys.argv[2], 'Loaded!')
        teku2Panda = pd.read_csv(teku2File)
        print(sys.argv[3], 'Loaded!')
        
        
    else:
        print("csv or logs must be specified on the first argument")
        exit()
    
    # Plot
    if csvORlogs != 'teku':
        plotMetricsFromPanda(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda)
    else: 
        plotTeku1vsTeku2(teku1Panda, teku2Panda,  'Current Slot', 'DISK' , 'Disk Usage on Teku Syncing in Different Time Moments', 'Disk Usage (GB)', 'Last Synced Slot', 4, 20)
    print("Script Done!")
    
    
def addPeersSlotsToPanda(panda1, panda2, time1, time2, column1, column2):
    panda2index = 0
    column1array = []
    column2array = []
    for index, row in panda1.iterrows():
        if index == 0:
            column1array.append(panda2.iloc[panda2index][column1])
            column2array.append(panda2.iloc[panda2index][column2])
            
        elif panda1.iloc[index][time1] < panda2.iloc[panda2index][time2]:
            column1array.append(panda2.iloc[panda2index][column1])
            column2array.append(panda2.iloc[panda2index][column2])
        else:
            try:
                panda2index = panda2index + 1
                column1array.append(panda2.iloc[panda2index][column1])
                column2array.append(panda2.iloc[panda2index][column2])
            except:
                panda2index = panda2index - 1
                column1array.append(panda2.iloc[panda2index][column1])
                column2array.append(panda2.iloc[panda2index][column2])

    panda1[column1] = column1array
    panda1[column2] = column2array
    

def getMetricsFromFile(clientType, inputFile):
    startingTime = 0
    startingNetOut = 0
    startingNetIn = 0
    
    # Lodestar Bias removed
    prevDiskValue = 0
    prevDiskBiasValue = 0
    totalBiasDiff = 0
    totalDiskIncrease = 0
    auxCount = 0
    averageDiskIncrease = 0
    biasTimeStart = 1604871411 # 2020-Nov-08 22:36:51
    biasTimeFinish = 1604872160 # 2020-Nov-0 8 22:49:20
    #biasSize = 9343.5 # Size of the folder Downloaded (MB)
    
    # Degfine the dictionary that later will be the the panda
    clientMetrics = {'TIME': [], 'MEM': [], 'CPU': [], 'NETOUT': [], 'NETIN': [], 'DISK': []}
    
    f = open(inputFile, 'r')
    lines = f.readlines()
    # close the file
    f.close()
    
    # Iterate through the lines on the file
    for line in lines:
        if ("Something went wrong" in line) or ("Error" in line) or ('Pid' in line) or ('Monitoring' in line) or ('The size' in line) or ('TIME' in line) or('Welcome' in line) or('.eth2' in line):
            continue
        parameters = line.split(" , ")
        
        # Get the date in secs from the lighthouse format
        if clientType == 'lighthouse':
            timeRaw = datetime.strptime(parameters[0], '%B %d %H:%M:%S:%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the teku format
        if clientType == 'teku':
            parameters[0] = parameters[0].replace('+01:00', '')
            timeRaw = datetime.strptime(parameters[0], '%Y-%m-%d %H:%M:%S.%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the nimbus format
        if clientType == 'nimbus':
            timeRaw = datetime.strptime(parameters[0], '%Y-%m-%d %H:%M:%S.%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the nimbus format
        if clientType == 'prysm':
            timeRaw = datetime.strptime(parameters[0], '%Y-%b-%d %H:%M:%S')
            timeSecs =timeRaw.timestamp()
        # Get the date in secs from the lodestar format
        if clientType == 'lodestar':
            timeRaw = datetime.strptime(parameters[0], '%Y-%b-%d %H:%M:%S')
            timeSecs =timeRaw.timestamp()
            
        # get the starting point
        if startingTime == 0:
            startingTime = timeSecs
            startingNetOut = float(parameters[3])
            startingNetIn = float(parameters[4])
        
        
        timeMins = (timeSecs - startingTime)/60 # We convert them to minutes
        netOut = (float(parameters[3]) - startingNetOut)
        netIn = (float(parameters[4]) - startingNetIn)
        
        # Lodestar Bias Remove
        if clientType == 'lodestar':
            if auxCount == 0:
                startingTimeOfLodestar = timeSecs
            if timeSecs < biasTimeStart:
                auxCount = auxCount + 1
                totalDiskIncrease = totalDiskIncrease + (netOut - prevDiskValue)
                #print('BaseTime:', startingTimeOfLodestar)
                #print('startTime:', biasTimeStart, 'currentTime:', timeSecs)
                #print('totalDiskIncrease:', totalDiskIncrease)
                #print ('CNT:', auxCount)
                netOut = totalDiskIncrease
                prevDiskValue = netOut
                prevDiskBiasValue = prevDiskValue
            if timeSecs >= biasTimeStart and timeSecs <= biasTimeFinish:
                averageDiskIncrease =  totalDiskIncrease / auxCount 
                totalBiasDiff = (netOut - totalDiskIncrease)
                #print('net', netOut,'prev',prevDiskBiasValue)
                netOut = prevDiskBiasValue + averageDiskIncrease
                #print(netOut)
                #print('Average:', averageDiskIncrease)
                #print('TotalBias:', totalBiasDiff)
                prevDiskBiasValue = netOut
            if timeSecs > biasTimeFinish:
                #print('Prev:', prevDiskBiasValue)
                netOut = netOut - totalBiasDiff
                print('net:', netOut)
                
        
        # Append values to the clientMetrics dict
        clientMetrics['TIME'].append(timeMins/60)
        clientMetrics['MEM'].append(float(parameters[1])/1000)
        clientMetrics['CPU'].append(float(parameters[2]))
        clientMetrics['NETOUT'].append(netOut/1000)
        clientMetrics['NETIN'].append(netIn/1000)
        clientMetrics['DISK'].append((float(parameters[5].replace('\n', '')))/1000)
    
    
    metricsPanda = pd.DataFrame(data = clientMetrics, columns = ['TIME','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
    return metricsPanda

def plotTeku1vsTeku2(teku1, teku2, xMetrics, yMetrics, title, ylabel, xlabel, loc, size):
    outfile = '../../figures/metrics_plots/' + 'teku' + yMetrics + '-' + xMetrics + 'Comparison.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Teku 1'
    label2 = 'Teku 2'
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.05, label=label1)
    teku2.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label2)

    ax1.set_ylabel(ylabel, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.get_legend().remove()
    l1 = ax1.legend(markerscale=10, loc=loc, ncol=1, prop={'size':size})
    
    plt.axvline(x=73.349, color='r', linestyle='--')
    #plt.text(x=75, y=15, s='Slot 73.349 (08/14/2020 5:30pm (UTC))', rotation=90, color='r')
    plt.axvline(x=117.944, color='r', linestyle='--')
    #plt.text(x=120, y=15, s='Slot 117.944 (08/20/2020 22:09pm (UTC))', rotation=90, color='r')
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel(xlabel, fontsize = size)
    #ax1.xaxis.set_ticks(np.arange(0, teku1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
def plotMetricsFromPanda(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda):
    lightColor = 'tab:blue'
    tekuColor = 'tab:orange'
    NimbusColor = 'tab:green'
    PrysmColor = 'tab:red'
    LodestarColor = 'tab:purple'
    
    SyncColor = 'k'
    PeersColor = 'tab:grey'
    
    fontSize = 20

    # Lighthouse CPU-DISK
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lighthouse CPU Usage VS Disk Usage", "CPU Usage (%)", "Disk Usage (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse CPU-NETIN
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lighthouse CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse CPU-PEeRS
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'Peers Connected', "Lighthouse CPU Usage VS Peers Connected", "CPU Usage (%)", "Peers Connected", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse MEM-DISK
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'MEM', 'TIME', 'DISK', "Lighthouse System Memory Usage VS Disk Usage", "System Memory Used (GB)", "Disk Usage (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse DISK-NETIN
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'DISK', 'TIME', 'NETIN', "Lighthouse Disk Usage VS Network Incoming Traffic", "Disk Usage (GB)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse MEM-NETOUT
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'MEM', 'TIME', 'NETOUT', "Lighthouse System Memory Usage VS Network Outcoming Traffic", "System Memory Used (GB)", "Network Outcoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    
    # Prysm CPU-NETIN
    plotCpuVS('prysm', prysmPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Prysm CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", PrysmColor, SyncColor, 4, 2, fontSize)
    # Lodestar CPU-NETOUT
    plotCpuVS('lodestar', lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lodestar CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", LodestarColor, SyncColor, 4, 2, fontSize)
     
     
    # Plot MEM-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'MEM', 'TIME', 'Current Slot', "Lighthouse System Memory Usage VS Chain Synchronization", "System Memory Used (GB)", "Last synced slot (thousands)", lightColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('teku', tekuPanda, 'TIME', 'MEM', 'TIME', 'Current Slot', "Teku System Memory Usage VS Chain Synchronization", "System Memory Used (GB)", "Last synced slot  (thousands)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('nimbus', nimbusPanda, 'TIME', 'MEM', 'TIME', 'Current Slot', "Nimbus System Memory Usage VS Chain Synchronization", "System Memory Used (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, 'TIME', 'MEM', 'TIME', 'Current Slot', "Prysm System Memory Usage VS Chain Synchronization", "System Memory Used (GB)", "Last synced slot (thousands)", PrysmColor, SyncColor , 4, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, 'TIME', 'MEM', 'TIME', 'Current Slot', "Lodestar System Memory Usage VS Chain Synchronization", "System Memory Used (GB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 4, 2, fontSize)
  
    # Plot CPU-SYNC on the 5 clients
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'Current Slot', "Lighthouse CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)", lightColor, SyncColor , 2, 2, fontSize)
    plotCpuVS('teku', tekuPanda, 'TIME', 'CPU', 'TIME', 'Current Slot', "Teku CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, 'TIME', 'CPU', 'TIME', 'Current Slot', "Nimbus CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, 'TIME', 'CPU', 'TIME', 'Current Slot', "Prysm CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, 'TIME', 'CPU', 'TIME', 'Current Slot', "Lodestar CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETIN-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'NETIN', 'TIME', 'Current Slot', "Lighthouse Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('teku', tekuPanda, 'TIME', 'NETIN', 'TIME', 'Current Slot', "Teku Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , tekuColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('nimbus', nimbusPanda, 'TIME', 'NETIN', 'TIME', 'Current Slot', "Nimbus Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, 'TIME', 'NETIN', 'TIME', 'Current Slot', "Prysm Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, 'TIME', 'NETIN', 'TIME', 'Current Slot', "Lodestar Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETOUT-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'NETOUT', 'TIME', 'Current Slot', "Lighthouse Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('teku', tekuPanda, 'TIME', 'NETOUT', 'TIME', 'Current Slot', "Teku Network Outcoming Traffic VS Chain Synchronization", "Network IncomiOutcomingng Traffic (GB)", "Last synced slot (thousands)", tekuColor, SyncColor, 2, 2, fontSize )
    plotSyncVS('nimbus', nimbusPanda, 'TIME', 'NETOUT', 'TIME', 'Current Slot', "Nimbus Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, 'TIME', 'NETOUT', 'TIME', 'Current Slot', "Prysm Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, 'TIME', 'NETOUT', 'TIME', 'Current Slot', "Lodestar Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot DISK-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, 'TIME', 'DISK', 'TIME', 'Current Slot', "Lighthouse Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('teku', tekuPanda, 'TIME', 'DISK', 'TIME', 'Current Slot', "Teku Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)", tekuColor, SyncColor, 4, 2, fontSize )
    plotSyncVS('nimbus', nimbusPanda, 'TIME', 'DISK', 'TIME', 'Current Slot', "Nimbus Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, 'TIME', 'DISK', 'TIME', 'Current Slot', "Prysm Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, 'TIME', 'DISK', 'TIME', 'Current Slot', "Lodestar Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 4, 2, fontSize)
    
    # Plot CPU-DISK on the 5 clients
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lighthouse CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", lightColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('teku', tekuPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Teku CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Nimbus CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", NimbusColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Prysm CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lodestar CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot CPU-NETIN on the 5 clients
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lighthouse CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize )
    plotCpuVS('teku', tekuPanda, 'TIME', 'CPU','TIME', 'NETIN', "Teku CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", tekuColor, SyncColor , 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Nimbus CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Prysm CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lodestar CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot CPU-NETOUT on the 5 clients
    plotCpuVS('lighthouse', lightPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lighthouse CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", lightColor, SyncColor , 2, 2, fontSize)
    plotCpuVS('teku', tekuPanda, 'TIME', 'CPU','TIME', 'NETOUT', "Teku CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Nimbus CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", NimbusColor, SyncColor , 4, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Prysm CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lodestar CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETIN-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, 'TIME', 'NETIN', 'TIME', 'Peers Connected', "Lighthouse Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('teku', tekuPanda, 'TIME', 'NETIN', 'TIME', 'Peers Connected', "Teku Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('nimbus', nimbusPanda, 'TIME', 'NETIN', 'TIME', 'Peers Connected', "Nimbus Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('prysm', prysmPanda, 'TIME', 'NETIN', 'TIME', 'Peers Connected', "Prysm Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('lodestar', lodestarPanda, 'TIME', 'NETIN', 'TIME', 'Peers Connected', "Lodestar Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 2, 2, fontSize)
    
    # Plot NETOUT-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, 'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Lighthouse Network Outcoming Traffic VS Chain Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('teku', tekuPanda, 'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Teku Network Outcoming Traffic VS Chain Peers Connected", "Network IncomiOutcomingng Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('nimbus', nimbusPanda, 'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Nimbus Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('prysm', prysmPanda, 'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Prysm Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('lodestar', lodestarPanda, 'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Lodestar Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 4, 2, fontSize)
    
    
    # Plot 5 client MEM on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'MEM', "System Memory Usage. Comparison Between Clients", "System Memory Used (GB)", 4, fontSize)

    
    # Plot 5 client CPU on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'Current Slot', "CPU Usage. Comparison Between Clients", "CPU Usage (%)", 4, fontSize)
    
    
    # Plot 5 client NETIN on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'NETIN', "Network Incoming Traffic. Comparison Between Clients", "Network Incoming Traffic (GB)", 2, fontSize)
    
    
    # Plot 5 client NETOUT on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'NETOUT', "Network Outcoming Traffic. Comparison Between Clients", "Network Outcoming Traffic (GB)", 2, fontSize)
  
    
    # Plot 5 client DISK on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'DISK', "Disk Usage. Comparison Between Clients", "Disk Usage (GB)", 2, fontSize)
    
    # Plot 5 client NETIN-PEERS on the same graph
    plotAllClients(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'NETIN', 'TIME', 'Peers Connected', "Network Incoming Traffic VS Peers Connected. Comparison Between Clients", "Network Incoming Traffic (GB)", "Peers Connected", 1, fontSize)
    
    # Plot 5 client NETOUT-PEERS on the same graph
    plotAllClients(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, 
              'TIME', 'NETOUT', 'TIME', 'Peers Connected', "Network Outcoming Traffic VS Peers Connected. Comparison Between Clients", "Network Outcoming Traffic (GB)Me", "Peers Connected", 1, fontSize)
    
    
    # Plot 5 client PEERS on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda,'TIME', 'Peers Connected', "Peers Connected. Comparison Between Clients", "Peers Connected", 1, fontSize)
    
    # Plot 5 client Sync on the same graph
    plotAllClientsOnly(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda,'TIME', 'Current Slot', "Chain Synchronization. Comparison Between Clients", "Current Slot (thousands)", 4, fontSize)
    
    # Plot 5 client Sync on the same graph
    plotAllClientsOnlyRange(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda,'TIME', 'Current Slot', 12, 150, "Chain Synchronization. Comparison Between Clients", "Current Slot (thousands)", 4, fontSize)

    # Plot 5 client DISK-SLOT (On X axis) on the same graph
    plotAllClientsOnlySlot(lightPanda, tekuPanda, nimbusPanda, prysmPanda, lodestarPanda, "Range", 'Current Slot', 'DISK',  "Disk Usage Based on Last Synced Slot. Comparison Between Clients", "Disk Usage (GB)", 1, fontSize)
          
          
def plotSyncVS(clientName, pandaClientMetrics, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):

    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaClientMetrics.plot(ax=ax12, x=xSync, y=ySync, marker='.', markersize=0.05, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.get_legend().remove()
    #ax1.legend(markerscale=10., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.get_legend().remove()
    #ax12.legend(markerscale=30., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaClientMetrics[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show() 

    
def plotPeersVS(clientName, pandaClientMetrics, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
    
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync    
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaClientMetrics.plot(ax=ax12, x=xSync, y=ySync, style='.',  marker='.', markersize=0.4, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.get_legend().remove()
    #ax1.legend(markerscale=10., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.get_legend().remove()
    #ax12.legend(markerscale=30., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaClientMetrics[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()
    
    
def plotCpuVS(clientName, pandaClientMetrics, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync    
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, style='.', marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaClientMetrics.plot(ax=ax12, x=xSync, y=ySync,  marker='.', markersize=0.2, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.get_legend().remove()
    #ax1.legend(markerscale=30., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.get_legend().remove()
    #ax12.legend(markerscale=10., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaClientMetrics[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()
    
def plotAllClients(light1, teku1, nimbus1, prysm1, lodestar1, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, loc, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse'
    label2 = 'Teku'
    label3 = 'Nimbus' 
    label4 = 'Prysm'
    label5 = 'Lodestar' 
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.2, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label5)
    
    ax12 = ax1.twinx()
    light1.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label1)
    teku1.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label2)
    nimbus1.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label3)
    prysm1.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label4)
    lodestar1.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label5)    

    ax1.set_ylabel(y1label, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    #ax1.get_legend().remove()
    l1 = ax1.legend(markerscale=10, loc=loc, ncol=1, prop={'size':size})
    
    ax12.set_ylabel(y2label, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelsize = size)
    ax12.get_legend().remove()
    #l2 = ax12.legend(markerscale=30., loc=2 , ncol=ncol, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, prysm1[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()
    
def plotSingleSerieOfPanda(panda, xMetrics, yMetrics, title, ylabel, xlabel, size):
    
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse' + ' ' + yMetrics
    label2 = 'Teku' +  ' ' + yMetrics
    label3 = 'Nimbus' +  ' ' + yMetrics 
    label4 = 'Prysm' +  ' ' + yMetrics 
    label5 = 'Lodestar' +  ' ' + yMetrics 
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.05, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label5)

    ax1.set_ylabel(y1label, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.get_legend().remove()
    #l1 = ax1.legend(markerscale=10, loc=1, ncol=ncol, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, prysm1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()
    
def plotAllClientsOnlySlot(light1, teku1, nimbus1, prysm1, lodestar1, sliceRange, xMetrics, yMetrics, title, ylabel, loc, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + xMetrics + '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse'
    label2 = 'Teku'
    label3 = 'Nimbus' 
    label4 = 'Prysm'
    label5 = 'Lodestar'
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.05, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label5)

    ax1.set_ylabel(ylabel, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    #ax1.get_legend().remove()
    l1 = ax1.legend(markerscale=10, loc=loc, ncol=1, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    if (xMetrics == 'Current Slot'):
    	plt.axvline(x=73.349, color='r', linestyle='--')
    	plt.text(x=75, y=13, s='Slot 73.349 (08/14/2020 5:30pm (UTC))', rotation=90, color='r')
    	plt.axvline(x=117.944, color='r', linestyle='--')
    	plt.text(x=120, y=13, s='Slot 117.944 (08/20/2020 22:09pm (UTC))', rotation=90, color='r')
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Last Synced Slot (thousands)", fontsize = size)
    #ax1.xaxis.set_ticks(np.arange(0, prysm1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()
    
def plotAllClientsOnly(light1, teku1, nimbus1, prysm1, lodestar1, xMetrics, yMetrics, title, y1label, loc, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse'
    label2 = 'Teku'
    label3 = 'Nimbus' 
    label4 = 'Prysm'
    label5 = 'Lodestar'
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.05, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label5)

    ax1.set_ylabel(y1label, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    #ax1.get_legend().remove()
    l1 = ax1.legend(markerscale=10, loc=loc, ncol=1, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, prysm1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()

def plotAllClientsOnlyRange(light1, teku1, nimbus1, prysm1, lodestar1, xMetrics, yMetrics, xLimit, yLimit, title, y1label, loc, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + 'Ranged.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse'
    label2 = 'Teku'
    label3 = 'Nimbus' 
    label4 = 'Prysm'
    label5 = 'Lodestar'
    
    fig = plt.figure(figsize=(10,6))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.05, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.05, label=label5)

    ax1.set_ylabel(y1label, fontsize = size)
    ax1.set_xbound(lower=0, upper=xLimit)
    ax1.set_xlim(emit=True, left=0, right=xLimit)
    ax1.set_ylim(bottom=0, top=yLimit)
    llimit, rlimit = ax1.get_xlim()
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    #ax1.get_legend().remove()
    l1 = ax1.legend(markerscale=10, loc=loc, ncol=1, prop={'size':size-3})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    if (xMetrics == 'TIME' or xMetrics == 'Current Slot'):
    	ax1.axhline(y=73.349, color='r', linestyle='--')
    	ax1.axhline(y=117.944, color='r', linestyle='--')
    
    ax1.grid(which='major', axis='both', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    #ax1.xaxis.set_ticks(np.arange(0, prysm1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    #plt.show()

main()

