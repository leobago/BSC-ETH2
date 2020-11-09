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
    
    if csvORlogs == 'logs':
        # Generate panda from lighthouse and create csv file
        lightPanda = getMetricsFromFile('lighthouse',lightFile)
        print("Lighthouse -> PandaObject : Done")
        lightP = Path(__file__).parent / '../../data/Lighthouse/lighthouseMetrics.csv' 
        lightPanda.to_csv(lightP)
        print("Created lighthouseMetrics.csv in data/Nimbus")
        
        # Generate panda from teku and create csv file
        tekuPanda  = getMetricsFromFile('teku',tekuFile)
        print("Teku -> PandaObject : Done")
        tekuP = Path(__file__).parent / '../../data/Teku/tekuMetrics.csv' 
        tekuPanda.to_csv(tekuP)
        print("Created tekuMetrics.csv in data/Nimbus")
        
        # Generate panda from nimbus and create csv file
        nimbusPanda = getMetricsFromFile('nimbus', nimbusFile)
        print("Nimbus -> PandaObject : Done")
        nimbusP = Path(__file__).parent / '../../data/Nimbus/nimbusMetrics.csv'
        nimbusPanda.to_csv(nimbusP)
        print("Created nimbusMetrics.csv in data/Nimbus")
        
        # Generate panda from prysm and create csv file
        prysmPanda = getMetricsFromFile('prysm', prysmFile)
        print("Prysm -> PandaObject : Done")
        prysmP = Path(__file__).parent / '../../data/Prysm/prysmMetrics.csv'
        prysmPanda.to_csv(prysmP)
        print("Created prysmMetrics.csv in data/Prysm")
        
        # Generate panda from lodestar and create csv file
        lodestarPanda = getMetricsFromFile('lodestar', lodestarFile)
        print("Lodestar -> PandaObject : Done")
        lodestarP = Path(__file__).parent / '../../data/Lodestar/lodestarMetrics.csv'
        lodestarPanda.to_csv(lodestarP)
        print("Created lodestarMetrics.csv in data/Lodestar")
        
    elif csvORlogs == 'csv':
        lightPanda = pd.read_csv(lightFile)
        tekuPanda = pd.read_csv(tekuFile)
        nimbusPanda = pd.read_csv(nimbusFile)
        prysmPanda = pd.read_csv(prysmFile)
        lodestarPanda = pd.read_csv(lodestarFile)
        
    else:
        print("csv or logs must be specified on the first argument")
        exit()
    
    # Read the CSV from the 5 clients and parse the data into a panda
    lightSyncPanda = pd.read_csv(lightSyncFile)
    tekuSyncPanda = pd.read_csv(tekuSyncFile)
    nimbusSyncPanda = pd.read_csv(nimbusSyncFile)
    prysmSyncPanda = pd.read_csv(prysmSyncFile)
    lodestarSyncPanda = pd.read_csv(lodestarSyncFile)
    
    print(lodestarSyncPanda)
    
    
    # Plot
    plotMetricsFromPanda(lightPanda,lightSyncPanda, tekuPanda,tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda)

    print("Script Done!")

def getMetricsFromFile(clientType, inputFile):
    startingTime = 0
    startingNetOut = 0
    startingNetIn = 0
    
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
        
        # Append values to the clientMetrics dict
        clientMetrics['TIME'].append(timeMins/60)
        clientMetrics['MEM'].append(float(parameters[1])/1000)
        clientMetrics['CPU'].append(float(parameters[2]))
        clientMetrics['NETOUT'].append(netOut/1000)
        clientMetrics['NETIN'].append(netIn/1000)
        clientMetrics['DISK'].append((float(parameters[5].replace('\n', '')))/1000)
    
    
    metricsPanda = pd.DataFrame(data = clientMetrics, columns = ['TIME','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
    return metricsPanda
    
def plotMetricsFromPanda(lightPanda, lightSyncPanda, tekuPanda, tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda):
    lightColor = 'tab:blue'
    tekuColor = 'tab:orange'
    NimbusColor = 'tab:green'
    PrysmColor = 'tab:red'
    LodestarColor = 'tab:purple'
    
    SyncColor = 'k'
    PeersColor = 'tab:grey'

    # Plot MEM-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Lighthouse MEM Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot", lightColor, SyncColor, 4, 2, 10)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Teku MEM Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot" , tekuColor, SyncColor, 4, 2, 10)
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Nimbus MEM Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot" , NimbusColor, SyncColor, 4, 2, 10)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Prysm MEM Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot", PrysmColor, SyncColor , 4, 2, 10)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Lodestar MEM Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot" , LodestarColor, SyncColor, 4, 2, 10)
  
    # Plot CPU-SYNC on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Lighthouse CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot", lightColor, SyncColor , 2, 2, 10)
    plotCpuVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Teku CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot" , tekuColor, SyncColor, 4, 2, 10)
    plotCpuVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Nimbus CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot" , NimbusColor, SyncColor, 2, 2, 10)
    plotCpuVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Prysm CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot" , PrysmColor, SyncColor, 2, 2, 10)
    plotCpuVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Lodestar CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot", LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot NETIN-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Lighthouse Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot" , lightColor, SyncColor, 2, 2, 10)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Teku Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot" , tekuColor, SyncColor, 2, 2, 10)
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Nimbus Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot" , NimbusColor, SyncColor, 2, 2, 10)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Prysm Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot" , PrysmColor, SyncColor, 2, 2, 10)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Lodestar Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot", LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot NETOUT-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Lighthouse Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot" , lightColor, SyncColor, 2, 2, 10)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Teku Network Outcoming Traffic VS Chain Synchronization", "Network IncomiOutcomingng Traffic (GB)", "Last synced slot", tekuColor, SyncColor, 2, 2, 10 )
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Nimbus Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot" , NimbusColor, SyncColor, 2, 2, 10)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Prysm Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot" , PrysmColor, SyncColor, 2, 2, 10)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Lodestar Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot" , LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot DISK-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Lighthouse Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot" , lightColor, SyncColor, 4, 2, 10)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Teku Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot", tekuColor, SyncColor, 4, 2, 10 )
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Nimbus Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot" , NimbusColor, SyncColor, 4, 2, 10)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Prysm Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot" , PrysmColor, SyncColor, 4, 2, 10)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Lodestar Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot" , LodestarColor, SyncColor, 4, 2, 10)
    
    # Plot CPU-DISK on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lighthouse CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", lightColor, SyncColor, 2, 2, 10 )
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Teku CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , tekuColor, SyncColor, 4, 2, 10)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Nimbus CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", NimbusColor, SyncColor, 2, 2, 10 )
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Prysm CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , PrysmColor, SyncColor, 2, 2, 10)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lodestar CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot CPU-NETIN on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lighthouse CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, 10 )
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU','TIME', 'NETIN', "Teku CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", tekuColor, SyncColor , 4, 2, 10)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Nimbus CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , NimbusColor, SyncColor, 4, 2, 10)
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Prysm CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, 10)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lodestar CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot CPU-NETOUT on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lighthouse CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", lightColor, SyncColor , 2, 2, 10)
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU','TIME', 'NETOUT', "Teku CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , tekuColor, SyncColor, 4, 2, 10)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Nimbus CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", NimbusColor, SyncColor , 4, 2, 10)
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Prysm CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, 10)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lodestar CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, 10)
    
    # Plot NETIN-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Lighthouse Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, 10)
    plotPeersVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Teku Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, 10)
    plotPeersVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Nimbus Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, 10)
    plotPeersVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Prysm Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, 10)
    plotPeersVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Lodestar Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 2, 2, 10)
    
    # Plot NETOUT-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Lighthouse Network Outcoming Traffic VS Chain Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, 10)
    plotPeersVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Teku Network Outcoming Traffic VS Chain Peers Connected", "Network IncomiOutcomingng Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, 10)
    plotPeersVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Nimbus Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, 10)
    plotPeersVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Prysm Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, 10)
    plotPeersVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Lodestar Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 4, 2, 10)
    
    
    # Plot 5 client MEM on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsMEM.png'
     # doble y axis test
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='MEM', marker='.', markersize=0.2, label='Lighthouse MEM')
    tekuPanda.plot(ax=ax, x='TIME', y='MEM', marker='.', markersize=0.2, label='Teku MEM')
    nimbusPanda.plot(ax=ax, x='TIME', y='MEM', marker='.', markersize=0.2, label='Nimbus MEM')
    prysmPanda.plot(ax=ax, x='TIME', y='MEM', marker='.', markersize=0.2, label='Prysm MEM')
    lodestarPanda.plot(ax=ax, x='TIME', y='MEM', marker='.', markersize=0.2, label='Lodestar MEM')
    ax.set_ylabel("System Memory Used by the client (MB)")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Lighthouse Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05,  label='Teku Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Nimbus Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05,  label='Prysm Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Lodestar Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
    
    plt.title("System Memory Usage VS Chain Synchronization. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=2, ncol=2, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)

    
    # Plot 5 client CPU on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsCPU.png'
    # doble y axis test
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='CPU',  style='.', marker=',', markersize=0.15, label='Lighthouse CPU')
    tekuPanda.plot(ax=ax, x='TIME', y='CPU',  style='.', marker=',', markersize=0.15, label='Teku CPU')
    nimbusPanda.plot(ax=ax, x='TIME', y='CPU', style='.', marker=',', markersize=0.15, label='Nimbus CPU')
    prysmPanda.plot(ax=ax, x='TIME', y='CPU', style='.', marker=',', markersize=0.15, label='Prysm CPU')
    lodestarPanda.plot(ax=ax, x='TIME', y='CPU', style='.', marker=',', markersize=0.15, label='Lodestar CPU')
    ax.set_ylabel("CPU Usage (%)")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.1, label='Lighthouse Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.1,  label='Teku Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.1, label='Nimbus Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.1,  label='Prysm Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',  marker=',', markersize=0.1, label='Lodestar Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
    
    plt.title("CPU Usage VS Chain Synchronization. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=2, ncol=1, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)
    
    
    # Plot 5 client NETIN on the same graph   
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsNETIN.png'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETIN', marker='.', markersize=0.2, label='Lighthouse NETIN')
    tekuPanda.plot(ax=ax, x='TIME', y='NETIN', marker='.', markersize=0.2, label='Teku NETIN')
    nimbusPanda.plot(ax=ax, x='TIME', y='NETIN', marker='.', markersize=0.2, label='Nimbus NETIN')
    prysmPanda.plot(ax=ax, x='TIME', y='NETIN', marker='.', markersize=0.2, label='Prysm NETIN')
    lodestarPanda.plot(ax=ax, x='TIME', y='NETIN', marker='.', markersize=0.2, label='Lodestar NETIN')
    ax.set_ylabel("Network Incoming Traffic (GB)")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Lighthouse   Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05,  label='Teku   Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Nimbus   Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05,  label='Prysm  Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05, label='Lodestar   Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
    
    plt.title("Network Incoming Traffic VS Chain Synchronization. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=2, ncol=2, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)
    
    
    # Plot 5 client NETOUT on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsNETOUT.png'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETOUT', marker='.', markersize=0.2, label='Lighthouse NETOUT')
    tekuPanda.plot(ax=ax, x='TIME', y='NETOUT', marker='.', markersize=0.2, label='Teku NETOUT')
    nimbusPanda.plot(ax=ax, x='TIME', y='NETOUT', marker='.', markersize=0.2, label='Nimbus NETOUT')
    prysmPanda.plot(ax=ax, x='TIME', y='NETOUT', marker='.', markersize=0.2, label='Prysm NETOUT')
    lodestarPanda.plot(ax=ax, x='TIME', y='NETOUT', marker='.', markersize=0.2, label='Lodestar NETOUT')
    ax.set_ylabel("Network Outcoming Traffic (GB)")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.',  marker=',', markersize=0.05, label='Lighthouse  Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05,  label='Teku  Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05, label='Nimbus  Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05,  label='Prysm  Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05, label='Lodestar  Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
    
    plt.title("Network Outcoming Traffic VS Chain Synchronization. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=4, ncol=2, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)
  
    
    # Plot 5 client DISK on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsDISK.png'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='DISK', marker='.', markersize=0.2, label='Lighthouse DISK')
    tekuPanda.plot(ax=ax, x='TIME', y='DISK', marker='.', markersize=0.2, label='Teku DISK')
    nimbusPanda.plot(ax=ax, x='TIME', y='DISK', marker='.', markersize=0.2, label='Nimbus DISK')
    prysmPanda.plot(ax=ax, x='TIME', y='DISK', marker='.', markersize=0.2, label='Prysm DISK')
    lodestarPanda.plot(ax=ax, x='TIME', y='DISK', marker='.', markersize=0.2, label='Lodestar DISK')
    ax.set_ylabel("Disk Usage (GB)")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Lighthouse Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05,  label='Teku Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot',style='.',  marker=',', markersize=0.05, label='Nimbus Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05,  label='Prysm Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.05, label='Lodestar Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
       
    plt.title("Disk Usage VS Chain Synchronization. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=4, ncol=2, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
    
    # Plot 5 client SYNC-PEERS on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/ClientsSYNC-PEERS.png'
    ax = lightSyncPanda.plot(figsize=(20,10), x='Time (hours)', y='Peers Connected', marker='.', markersize=0.05, label='Lighthouse  Peers Connected')
    tekuSyncPanda.plot(ax=ax, x='Time (hours)', y='Peers Connected', marker='.', markersize=0.05, label='Teku Peers Connected')
    nimbusSyncPanda.plot(ax=ax, x='Time (hours)', y='Peers Connected', marker='.', markersize=0.05, label='Nimbus  Peers Connected')
    prysmSyncPanda.plot(ax=ax, x='Time (hours)', y='Peers Connected', marker='.', markersize=0.05, label='Prysm  Peers Connected')
    lodestarSyncPanda.plot(ax=ax, x='Time (hours)', y='Peers Connected', marker='.', markersize=0.05, label='Lodestar  Peers Connected')
    ax.set_ylabel("Peers Connected")
    #ax.grid(True)
    
    ax2 = ax.twinx()
    lightSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', style='.', marker=',', markersize=0.2, label='Lighthouse Current Slot')
    tekuSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.2,  label='Teku Current Slot')
    nimbusSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.2, label='Nimbus Current Slot')
    prysmSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.2,  label='Prysm Current Slot')
    lodestarSyncPanda.plot(ax=ax2, x='Time (hours)', y='Current Slot', marker=',', markersize=0.2, label='Lodestar Current Slot')
    ax2.set_ylabel("Last synced slot")
    #ax2.grid(True)
       
    plt.title("Disk Usage VS Peers Connected. Comparison Between Clients")
    plt.xlabel("Time of syncing (hours)")
    plt.legend(loc=2, ncol=2, prop={'size':10})
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
    

def plotSyncVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
      
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    ax1 = pandaClientMetrics.plot(figsize=(20,10), x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax1.set_ylabel(y1label, color=y1Color)
    ax1.tick_params(axis='y', labelcolor=y1Color)
    #ax1.grid(True)
    
    label2 = clientName + ' ' + ySync
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync, color=y2Color, marker=',', markersize=0.1, label=label2)
    ax12.set_ylabel(y2label, color=y2Color)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color)
    #ax12.grid(True)
    
    ax1.set_xlabel("Time of syncing (hours)")
    ax1.set_title(title)
    plt.tight_layout()
    plt.legend(loc=loc, ncol=ncol, prop={'size':size})
    #plt.legendHandles[0]._sizes = [7]
    plt.savefig(figurePath)
    plt.show()
    
def plotPeersVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    ax1 = pandaClientMetrics.plot(figsize=(20,10), x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax1.set_ylabel(y1label, color=y1Color)
    ax1.tick_params(axis='y', labelcolor=y1Color)
    #ax1.grid(True)
    
    label2 = clientName +  ' ' +ySync
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync, color=y2Color, marker='.', markersize=0.1, label=label2)
    ax12.set_ylabel(y2label, color=y2Color)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color)
    #ax12.grid(True)
    
    ax1.set_xlabel("Time of syncing (hours)")
    ax1.set_title(title)
    plt.tight_layout()
    plt.legend(loc=loc, ncol=ncol, prop={'size':size})
    #plt.legendHandles[0]._sizes = [7]
    plt.savefig(figurePath)
    plt.show()
    
def plotCpuVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    ax1 = pandaClientMetrics.plot(figsize=(20,10), x=xMetrics, y=yMetrics, style='.', marker=',', markersize=0.25, color=y1Color, label=label1)
    ax1.set_ylabel(y1label, color=y1Color)
    ax1.tick_params(axis='y', labelcolor=y1Color)
    #ax1.grid(True)
    
    label2 = clientName + ' ' + ySync
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync, color=y2Color, marker='.', markersize=0.1, label=label2)
    ax12.set_ylabel(y2label, color=y2Color)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color)
    #ax12.grid(True)
    
    ax1.set_xlabel("Time of syncing (hours)")
    ax1.set_title(title)
    plt.tight_layout()
    plt.legend(loc=loc, ncol=ncol, prop={'size':size})
    #plt.legendHandles[0]._sizes = [7]
    plt.savefig(figurePath)
    plt.show()


main()

