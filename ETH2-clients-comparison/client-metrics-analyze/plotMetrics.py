import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from datetime import datetime
from datetime import datetime
import csv


def main ():
    lightFile = sys.argv[1]
    tekuFile = sys.argv[2]
    
    # Generate panda from lighthouse
    lightPanda = getMetricsFromFile('lighthouse',lightFile)
    print("Lighthouse -> PandaObject : Done")
    # Generate panda from teku
    tekuPanda  = getMetricsFromFile('teku',tekuFile)
    print("Teku -> PandaObject : Done")
    
    print(lightPanda)
    print(tekuPanda)
    
    # Plot
    plotMetricsFromPanda(lightPanda, tekuPanda)

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
        if ("Something went wrong" in line) or ("Error" in line) or ('Pid' in line) or ('Monitoring' in line) or ('The size' in line) or ('TIME' in line):
            continue
        parameters = line.split(" , ")
        
        # Get the date in secs from the lighthouse format
        if clientType == 'lighthouse':
            timeRaw = datetime.strptime(parameters[0], '%B %d %H:%M:%S:%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the teku format
        if clientType == 'teku':
            parameters[0] = parameters[0].replace('+01:00', '')
            timeRaw = datetime.strptime(parameters[0],'%Y-%m-%d %H:%M:%S.%f')
            timeSecs = timeRaw.timestamp()
        # Further place fror Prysm and nimbus
        
        # get the starting point
        if startingTime == 0:
            startingTime = timeSecs
            startingNetOut = float(parameters[3])
            startingNetIn = float(parameters[4])
        
        
        timeMins = (timeSecs - startingTime)/60 # We convert them to minutes
        netOut = (float(parameters[3]) - startingNetOut)
        netIn = (float(parameters[4]) - startingNetIn)
        
        # Append values to the clientMetrics dict
        clientMetrics['TIME'].append(timeMins)
        clientMetrics['MEM'].append(float(parameters[1]))
        clientMetrics['CPU'].append(float(parameters[2]))
        clientMetrics['NETOUT'].append(netOut)
        clientMetrics['NETIN'].append(netIn)
        clientMetrics['DISK'].append(float(parameters[5].replace('\n', '')))
    
    
    metricsPanda = pd.DataFrame(data = clientMetrics, columns = ['TIME','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
    return metricsPanda
    
def plotMetricsFromPanda(lightPanda, tekuPanda):
    # Plot MEM on the same graph
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='MEM', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='MEM', label='teku')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("System Memory Used by the client (MB)")
    plt.title("System Memory Usage Comparison Between Clients")
    plt.legend()
    plt.show()
    
    # Plot CPU on the same graph
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='CPU', style='.', marker='.', markersize=0.8, label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='CPU',style='.', marker='.', markersize=0.8, label='teku')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("CPU Usage (%)")
    plt.title("CPU Usage Comparison Between Clients")
    plt.legend()
    plt.show()
    
    # Plot NETIN on the same graph
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETIN', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='NETIN', label='teku')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("Network Incoming Traffic (MB)")
    plt.title("Network Incoming Traffic Comparison Between Clients")
    plt.legend()
    plt.show()
    
    # Plot NETOUT on the same graph
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='NETOUT', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='NETOUT', label='teku')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("Network Outcoming Traffic (MB)")
    plt.title("Network Outcoming Traffic Comparison Between Clients")
    plt.legend()
    plt.show()
    
    # Plot DISK on the same graph
    ax = lightPanda.plot(figsize=(20,10), x='TIME', y='DISK', label='Lighthouse')
    tekuPanda.plot(ax=ax, x='TIME', y='DISK', label='teku')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("Disk Usage (MB)")
    plt.title("Disk Usage Comparison Between Clients")
    plt.legend()
    plt.show()

main()

