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
        
        # Generate panda from teku and create csv file
        nimbusPanda = getMetricsFromFile('nimbus', nimbusFile)
        print("Nimbus -> PandaObject : Done")
        nimbusP = Path(__file__).parent / '../../data/Nimbus/nimbusMetrics.csv'
        nimbusPanda.to_csv(nimbusP)
        print("Created nimbusMetrics.csv in data/Nimbus")
        
        # Generate panda from teku and create csv file
        prysmPanda = getMetricsFromFile('prysm', prysmFile)
        print("Prysm -> PandaObject : Done")
        prysmP = Path(__file__).parent / '../../data/Prysm/prysmMetrics.csv'
        prysmPanda.to_csv(prysmP)
        print("Created nimbusMetrics.csv in data/Prysm")
        
    elif csvORlogs == 'csv':
        lightPanda = pd.read_csv(lightFile)
        tekuPanda = pd.read_csv(tekuFile)
        nimbusPanda = pd.read_csv(nimbusFile)
        prysmPanda = pd.read_csv(prysmFile)
        
    else:
        print("csv or logs must be specified on the first argument")
        exit()
    
    
    
    # Plot
    plotMetricsFromPanda(lightPanda, tekuPanda, nimbusPanda, prysmPanda)

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
            
        if clientType == 'prysm':
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
        clientMetrics['MEM'].append(float(parameters[1]/1000))
        clientMetrics['CPU'].append(float(parameters[2]))
        clientMetrics['NETOUT'].append(netOut/1000)
        clientMetrics['NETIN'].append(netIn/1000)
        clientMetrics['DISK'].append((float(parameters[5].replace('\n', '')))/1000)
    
    
    metricsPanda = pd.DataFrame(data = clientMetrics, columns = ['TIME','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
    return metricsPanda
    
def plotMetricsFromPanda(lightPanda, tekuPanda, nimbusPanda, prysmPanda):
    # Plot MEM on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/MEM.pdf'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='MEM', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='MEM', label='teku')
    nimbusPanda.plot(ax=ax, x='TIME', y='MEM', label='nimbus')
    prysmPanda.plot(ax=ax, x='TIME', y='MEM', label='prysm')
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("System Memory Used by the client (MB)")
    plt.title("System Memory Usage Comparison Between Clients")
    ax.grid(True)
    plt.legend()
    plt.savefig(figurePath)
    plt.show()
    
    # Plot CPU on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/CPU.pdf'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='CPU', style='.', marker='.', markersize=0.8, label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='CPU',style='.', marker='.', markersize=0.8, label='teku')
    nimbusPanda.plot(ax=ax, x='TIME', y='CPU',style='.', marker='.', markersize=0.8, label='nimbus')
    prysmPanda.plot(ax=ax, x='TIME', y='CPU',style='.', marker='.', markersize=0.8, label='prysm')
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage Comparison Between Clients")
    ax.grid(True)
    plt.legend(markerscale=20)
    plt.savefig(figurePath)
    plt.show()
    
    # Plot NETIN on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/NETIN.pdf'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETIN', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='NETIN', label='teku')
    nimbusPanda.plot(ax=ax, x='TIME', y='NETIN', label='nimbus')
    prysmPanda.plot(ax=ax, x='TIME', y='NETIN', label='prysm')
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("Network Incoming Traffic (GB)")
    plt.title("Network Incoming Traffic Comparison Between Clients")
    ax.grid(True)
    plt.legend()
    plt.savefig(figurePath)
    plt.show()
    
    # Plot NETOUT on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/NETOUT.pdf'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETOUT', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='NETOUT', label='teku')
    nimbusPanda.plot(ax=ax, x='TIME', y='NETOUT', label='nimbus')
    prysmPanda.plot(ax=ax, x='TIME', y='NETOUT', label='prysm')
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("Network Outcoming Traffic (GB)")
    plt.title("Network Outcoming Traffic Comparison Between Clients")
    ax.grid(True)
    plt.legend()
    plt.savefig(figurePath)
    plt.show()
    
    # Plot DISK on the same graph
    figurePath =  Path(__file__).parent / '../../figures/metrics_plots/DISK.pdf'
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='DISK', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='DISK', label='teku')
    nimbusPanda.plot(ax=ax, x='TIME', y='DISK', label='nimbus')
    prysmPanda.plot(ax=ax, x='TIME', y='DISK', label='prysm')
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("Disk Usage (GB)")
    plt.title("Disk Usage Comparison Between Clients")
    ax.grid(True)
    plt.legend()
    plt.savefig(figurePath)
    plt.show()

main()

