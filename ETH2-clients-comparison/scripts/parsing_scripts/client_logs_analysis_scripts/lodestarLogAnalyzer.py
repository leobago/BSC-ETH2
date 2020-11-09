import sys
import re
#from datetime import datetime
from datetime import datetime
import matplotlib.dates 
from pathlib import Path
import csv


def main ():
    simulationTime = 0
    # Since the slots and the peers are in separated logs, we have to acumulate them
    peers = 0
    currentSlot = 0
    logFile = Path(__file__).parent / sys.argv[1]
    csvFile = Path(__file__).parent / sys.argv[2]

    print("Opening Lodestar File")
    with open(logFile) as f:
        logs = f.readlines()
    
    print("Opening Lodestar CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        csvwriter.writerow(["Time (hours)", "Current Slot", "Peers Connected"])
        
        # get the starting time
        firstSlice = logs[0].split('[')
        logTime = firstSlice[0]
        timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S ')
        simulationTime = timeRaw.timestamp()
        
        # Iterate through the lines
        for line in logs:
             # remove whitespace characters like `\n` at the end of each line
            line.strip()
            
            if "Fetching blocks for" in line:
                # Get block
                firstSlice = line.split('[')
                for string in firstSlice:
                    if 'block' in string:
                        slices = string.split(' ')
                        for sslice in slices:
                            if '...' in sslice:
                                currentSlot = sslice.split('...')[1]
                
                # get the time
                logTime = firstSlice[0]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S ')
                timeSecs = timeRaw.timestamp()
                
                row = [float((timeSecs - simulationTime)/(60*60)), currentSlot, peers]
                csvwriter.writerow(row)
            
            if "Peer status" in line:
                # Get block
                firstSlice = line.split('[')
                for string in firstSlice:
                    if 'activePeers' in string:
                        slices = string.split(' ')
                        for sslice in slices:
                            if 'activePeers' in sslice:
                                peers = sslice.split('=')[1]
                                peers = peers.replace(',', '')
                
                # get the time
                logTime = firstSlice[0]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S ')
                timeSecs = timeRaw.timestamp()
                
                row = [float((timeSecs - simulationTime)/(60*60)), currentSlot, peers]
                csvwriter.writerow(row)
        
    print("Lodestar CSV Done")

main() 
