import sys
import re
#from datetime import datetime
from datetime import datetime
import matplotlib.dates 
from pathlib import Path
import csv


def main ():
    simulationTime = 0
    logFile = Path(__file__).parent / sys.argv[1]
    csvFile = Path(__file__).parent / sys.argv[2]

    print("Opening Prysm File")
    with open(logFile) as f:
        logs = f.readlines()
    
    print("Opening Prysm CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        csvwriter.writerow(["Time (hours)", "Current Slot", "Peers Connected"])
        
        # Iterate through the lines
        for line in logs:
             # remove whitespace characters like `\n` at the end of each line
            line.strip()
            # get the starting time
            if "Starting beacon node" in line:
                firstSlice = line.split('"')
                logTime = firstSlice[1]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S')
                simulationTime = timeRaw.timestamp()
            
            if "Processing block" in line:
                
                # Get block
                firstSlice = line.split('"')
                for string in firstSlice:
                    if 'block' in string:
                        slices = string.split(' ')
                        for sslice in slices:
                            if '/' in sslice:
                                currentSlot = sslice.split('/')[0]
                            if 'peers' in sslice:
                                peers = sslice.split('=')[1]
                
                # get the time
                logTime = firstSlice[1]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S')
                timeSecs = timeRaw.timestamp()
                
                row = [float((timeSecs - simulationTime)/(60*60)), int(currentSlot)/1000, peers]
                csvwriter.writerow(row)
        
    print("Prysm CSV Done")

main()
