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
        print("Created lighthouseMetrics.csv in data/Lighthouse")
        
        # Generate panda from teku and create csv file
        tekuPanda  = getMetricsFromFile('teku',tekuFile)
        print("Teku -> PandaObject : Done")
        tekuP = Path(__file__).parent / '../../data/Teku/tekuMetrics.csv' 
        tekuPanda.to_csv(tekuP)
        print("Created tekuMetrics.csv in data/Teku")
        
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
    
    fontSize = 20

    # Lighthouse CPU-DISK
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lighthouse CPU Usage VS Disk Usage", "CPU Usage (%)", "Disk Usage (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse CPU-NETIN
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lighthouse CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse CPU-NETIN
    plotCpuVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Peers Connected', "Lighthouse CPU Usage VS Peers Connected", "CPU Usage (%)", "Peers Connected", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse MEM-DISK
    plotSyncVS('lighthouse', lightPanda, lightPanda, 'TIME', 'MEM', 'TIME', 'DISK', "Lighthouse System Memory Usage VS Disk Usage", "System Memory Used (MB)", "Disk Usage (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse DISK-NETIN
    plotSyncVS('lighthouse', lightPanda, lightPanda, 'TIME', 'DISK', 'TIME', 'NETIN', "Lighthouse Disk Usage VS Network Incoming Traffic", "Disk Usage (GB)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    # Lighthouse MEM-NETOUT
    plotSyncVS('lighthouse', lightPanda, lightPanda, 'TIME', 'MEM', 'TIME', 'NETOUT', "Lighthouse System Memory Usage VS Network Outcoming Traffic", "System Memory Used (MB)", "Network Outcoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize)
    
    # Prysm CPU-NETIN
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Prysm CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", PrysmColor, SyncColor, 4, 2, fontSize)
    # Lodestar CPU-NETOUT
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lodestar CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", LodestarColor, SyncColor, 4, 2, fontSize)
     
     
    # Plot MEM-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Lighthouse System Memory Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot (thousands)", lightColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Teku System Memory Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot  (thousands)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Nimbus System Memory Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Prysm System Memory Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot (thousands)", PrysmColor, SyncColor , 4, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'MEM', 'Time (hours)', 'Current Slot', "Lodestar System Memory Usage VS Chain Synchronization", "System Memory Used (MB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 4, 2, fontSize)
  
    # Plot CPU-SYNC on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Lighthouse CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)", lightColor, SyncColor , 2, 2, fontSize)
    plotCpuVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Teku CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Nimbus CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Prysm CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'CPU', 'Time (hours)', 'Current Slot', "Lodestar CPU Usage VS Chain Synchronization", "CPU Usage (%)", "Last synced slot (thousands)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETIN-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Lighthouse Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Teku Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , tekuColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Nimbus Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Prysm Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Lodestar Network Incoming Traffic VS Chain Synchronization", "Network Incoming Traffic (GB)", "Last synced slot (thousands)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETOUT-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Lighthouse Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Teku Network Outcoming Traffic VS Chain Synchronization", "Network IncomiOutcomingng Traffic (GB)", "Last synced slot (thousands)", tekuColor, SyncColor, 2, 2, fontSize )
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Nimbus Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Prysm Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Lodestar Network Outcoming Traffic VS Chain Synchronization", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot DISK-SYNC on the 5 clients
    plotSyncVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Lighthouse Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , lightColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Teku Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)", tekuColor, SyncColor, 4, 2, fontSize )
    plotSyncVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Nimbus Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Prysm Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , PrysmColor, SyncColor, 4, 2, fontSize)
    plotSyncVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Lodestar Disk Usage VS Chain Synchronization", "Disk Usage (GB)", "Last synced slot (thousands)" , LodestarColor, SyncColor, 4, 2, fontSize)
    
    # Plot CPU-DISK on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lighthouse CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", lightColor, SyncColor, 2, 2, fontSize )
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Teku CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Nimbus CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", NimbusColor, SyncColor, 2, 2, fontSize )
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Prysm CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'DISK', "Lodestar CPU Usage VS Disk usage", "CPU Usage (%)", "Disk usage (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot CPU-NETIN on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lighthouse CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", lightColor, SyncColor, 4, 2, fontSize )
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU','TIME', 'NETIN', "Teku CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", tekuColor, SyncColor , 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Nimbus CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , NimbusColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Prysm CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETIN', "Lodestar CPU Usage VS Network Incoming Traffic", "CPU Usage (%)", "Network Incoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot CPU-NETOUT on the 5 clients
    plotCpuVS('lighthouse', lightPanda, lightPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lighthouse CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", lightColor, SyncColor , 2, 2, fontSize)
    plotCpuVS('teku', tekuPanda, tekuPanda, 'TIME', 'CPU','TIME', 'NETOUT', "Teku CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , tekuColor, SyncColor, 4, 2, fontSize)
    plotCpuVS('nimbus', nimbusPanda, nimbusPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Nimbus CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", NimbusColor, SyncColor , 4, 2, fontSize)
    plotCpuVS('prysm', prysmPanda, prysmPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Prysm CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)" , PrysmColor, SyncColor, 2, 2, fontSize)
    plotCpuVS('lodestar', lodestarPanda, lodestarPanda, 'TIME', 'CPU', 'TIME', 'NETOUT', "Lodestar CPU Usage VS Network Outcoming Traffic", "CPU Usage (%)", "Network Outcoming Traffic (GB)", LodestarColor, SyncColor, 2, 2, fontSize)
    
    # Plot NETIN-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Lighthouse Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Teku Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Nimbus Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Prysm Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETIN', 'Time (hours)', 'Peers Connected', "Lodestar Network Incoming Traffic VS Peers Connected", "Network Incoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 2, 2, fontSize)
    
    # Plot NETOUT-PEERS on the 5 clients
    plotPeersVS('lighthouse', lightPanda, lightSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Lighthouse Network Outcoming Traffic VS Chain Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected", lightColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('teku', tekuPanda, tekuSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Teku Network Outcoming Traffic VS Chain Peers Connected", "Network IncomiOutcomingng Traffic (GB)", "Peers Connected", tekuColor, PeersColor , 4, 2, fontSize)
    plotPeersVS('nimbus', nimbusPanda, nimbusSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Nimbus Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , NimbusColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('prysm', prysmPanda, prysmSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Prysm Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , PrysmColor, PeersColor, 4, 2, fontSize)
    plotPeersVS('lodestar', lodestarPanda, lodestarSyncPanda, 'TIME', 'NETOUT', 'Time (hours)', 'Peers Connected', "Lodestar Network Outcoming Traffic VS Peers Connected", "Network Outcoming Traffic (GB)", "Peers Connected" , LodestarColor, PeersColor, 4, 2, fontSize)
    
    
    # Plot 5 client MEM on the same graph
    plotAllClients(lightPanda, lightSyncPanda, tekuPanda, tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda, 
              'TIME', 'MEM', 'Time (hours)', 'Current Slot', "System Memory Usage VS Chain Synchronization. Comparison Between Clients", "System Memory Used by the client (MB)", "Last synced slot (thousands)", 1, fontSize)

    
    # Plot 5 client CPU on the same graph
    plotAllClients(lightSyncPanda, lightPanda, tekuSyncPanda, tekuPanda, nimbusSyncPanda, nimbusPanda, prysmSyncPanda, prysmPanda, lodestarSyncPanda, lodestarPanda, 
              'Time (hours)', 'Current Slot', 'TIME', 'CPU', "CPU Usage VS Chain Synchronization. Comparison Between Clients", "Last synced slot (thousands)", "CPU Usage (%)", 1, fontSize)
    
    
    # Plot 5 client NETIN on the same graph
    plotAllClients(lightPanda, lightSyncPanda, tekuPanda, tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda, 
              'TIME', 'NETIN', 'Time (hours)', 'Current Slot', "Network Incoming Traffic VS Chain Synchronization. Comparison Between Clients", "Network Incoming Traffic (GB)", "Last synced slot (thousands)", 1, fontSize)
    
    
    # Plot 5 client NETOUT on the same graph
    plotAllClients(lightPanda, lightSyncPanda, tekuPanda, tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda, 
              'TIME', 'NETOUT', 'Time (hours)', 'Current Slot', "Network Outcoming Traffic VS Chain Synchronization. Comparison Between Clients", "Network Outcoming Traffic (GB)", "Last synced slot (thousands)", 1, fontSize)
  
    
    # Plot 5 client DISK on the same graph
    plotAllClients(lightPanda, lightSyncPanda, tekuPanda, tekuSyncPanda, nimbusPanda, nimbusSyncPanda, prysmPanda, prysmSyncPanda, lodestarPanda, lodestarSyncPanda, 
              'TIME', 'DISK', 'Time (hours)', 'Current Slot', "Disk Usage VS Chain Synchronization. Comparison Between Clients", "Disk Usage (GB)", "Last synced slot (thousands)", 1, fontSize)
    
    
    
    # Plot 5 client PEERS on the same graph
    plotAllClientsOnly(lightSyncPanda, tekuSyncPanda, nimbusSyncPanda, prysmSyncPanda, lodestarSyncPanda,'Time (hours)', 'Peers Connected', "Peers Connected. Comparison Between Clients", "Peers Connected", 1, fontSize)
    
    

def plotSyncVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):

    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync
    
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync, marker='.', markersize=0.05, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.legend(markerscale=10., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.legend(markerscale=30., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaSyncClient[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show() 

    
def plotPeersVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
    
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync    
    
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync, style='.',  marker='.', markersize=0.2, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.legend(markerscale=10., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.legend(markerscale=30., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaSyncClient[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
    
def plotCpuVS(clientName, pandaClientMetrics, pandaSyncClient, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, y1Color, y2Color, loc, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + clientName + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = clientName + ' ' + yMetrics
    label2 = clientName +  ' ' +ySync    
    
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(111)
    pandaClientMetrics.plot(ax=ax1, x=xMetrics, y=yMetrics, style='.', marker='.', markersize=0.2, color=y1Color, label=label1)
    ax12 = ax1.twinx()
    pandaSyncClient.plot(ax=ax12, x=xSync, y=ySync,  marker='.', markersize=0.2, color=y2Color, label=label2)    
    
    ax1.set_ylabel(y1label, color=y1Color, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelcolor=y1Color, labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    ax1.legend(markerscale=30., loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, color=y2Color, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelcolor=y2Color, labelsize = size)
    ax12.legend(markerscale=10., loc=1, ncol=ncol, prop={'size':size})
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, pandaSyncClient[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
def plotAllClients(light1, light2, teku1, teku2, nimbus1, nimbus2, prysm1, prysm2, lodestar1, lodestar2, xMetrics, yMetrics, xSync, ySync, title, y1label, y2label, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + '-' + ySync+ '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse' + ' ' + yMetrics
    label2 = 'Teku' +  ' ' + yMetrics
    label3 = 'Nimbus' +  ' ' + yMetrics 
    label4 = 'Prysm' +  ' ' + yMetrics 
    label5 = 'Lodestar' +  ' ' + yMetrics 
    
    fig = plt.figure(figsize=(20,10))
    ax1 = fig.add_subplot(111)
    light1.plot(ax=ax1, x=xMetrics, y=yMetrics,  marker='.', markersize=0.2, label=label1)
    teku1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label2)
    nimbus1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label3)
    prysm1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label4)
    lodestar1.plot(ax=ax1, x=xMetrics, y=yMetrics, marker='.', markersize=0.2, label=label5)
    
    label1 = 'Lighthouse' + ' ' + ySync
    label2 = 'Teku' +  ' ' + ySync
    label3 = 'Nimbus' +  ' ' + ySync 
    label4 = 'Prysm' +  ' ' + ySync 
    label5 = 'Lodestar' +  ' ' + ySync 
    
    ax12 = ax1.twinx()
    light2.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label1)
    teku2.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label2)
    nimbus2.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label3)
    prysm2.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label4)
    lodestar2.plot(ax=ax12, x=xSync, y=ySync, style='.', marker='.', markersize=0.1, label=label5)    

    ax1.set_ylabel(y1label, fontsize = size)
    ax1.set_ylim(bottom=0)
    ax1.tick_params(axis='y', labelsize = size)
    ax1.tick_params(axis='x', labelsize = size)
    l1 = ax1.legend(markerscale=10, loc=2, ncol=ncol, prop={'size':size})
    
    ax12.set_ylabel(y2label, fontsize = size)
    ax12.set_ylim(bottom=0)
    ax12.tick_params(axis='y', labelsize = size)
    l2 = ax12.legend(markerscale=30., loc=1, ncol=ncol, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, prysm2[xSync].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()
    
def plotAllClientsOnly(light1, teku1, nimbus1, prysm1, lodestar1, xMetrics, yMetrics, title, y1label, ncol, size):
        
    outfile = '../../figures/metrics_plots/' + 'Clients' + yMetrics + '.png'
    figurePath =  Path(__file__).parent / outfile
    
    label1 = 'Lighthouse' + ' ' + yMetrics
    label2 = 'Teku' +  ' ' + yMetrics
    label3 = 'Nimbus' +  ' ' + yMetrics 
    label4 = 'Prysm' +  ' ' + yMetrics 
    label5 = 'Lodestar' +  ' ' + yMetrics 
    
    fig = plt.figure(figsize=(20,10))
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
    l1 = ax1.legend(markerscale=10, loc=1, ncol=ncol, prop={'size':size})
    
    #ax1.legend(handles=[l1, l2], title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left', prop={'size':size})
    #bbox_to_anchor=(1,0), loc="lower right"
    
    ax1.grid(which='major', axis='x', linestyle='--')
    ax1.set_xlabel("Time of syncing (hours)", fontsize = size)
    ax1.xaxis.set_ticks(np.arange(0, prysm1[xMetrics].iloc[-1]+1, 6.0))
    plt.title(title, fontsize = size)
    plt.tight_layout()
    plt.savefig(figurePath)
    plt.show()

main()

