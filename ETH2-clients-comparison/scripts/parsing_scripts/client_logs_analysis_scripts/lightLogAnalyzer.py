import sys
import re
#from datetime import datetime
from datetime import datetime
from pathlib import Path
import csv


def main ():
    headSlot = 0
    CurrentSlot = 0
    simulationTime = 0
    logFile = Path(__file__).parent / sys.argv[1]
    csvFile = Path(__file__).parent / sys.argv[2]

    print("Opening Lighthouse File")
    with open(logFile) as f:
        logs = f.readlines()
        
    print("Opening Lighthouse CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        
        csvwriter.writerow(["Time (hours)", "Current Slot", "Peers Connected"])
        
        # Iterate through the lines
        for line in logs:
            # get the starting time from the 
            if simulationTime == 0 and 'INFO' in line:
                # get the time
                logTime = line.split(' INFO')[0]
                timeRaw = datetime.strptime(logTime, '%b %d %H:%M:%S.%f')
                timeSecs = timeRaw.timestamp()
                simulationTime = timeSecs
            
             # remove whitespace characters like `\n` at the end of line
            line = line.strip()
            if "INFO Syncing" in line:
                # the line contains distance info
                if headSlot == 0:
                    # Get distance
                    firstSlice = line.split(',')
                    for string in firstSlice:
                        if 'distance' in string:
                            number = string.split(' ')
                            distance = int(number[2])
                            
                        if 'peer' in string:
                            peers = string.split(':')[1]
                    
                    headSlot = distance
                    currentSlot = headSlot - distance
                    simulationTime = timeSecs
                    # Increase the HeadSlot as every 12sec we receive a syncing message
                 
                else:
                    headSlot += 1
                    # Get distance
                    firstSlice = line.split(',')
                    for string in firstSlice:
                        if 'distance' in string:
                            number = string.split(' ')
                            distance = int(number[2])
                            
                        if 'peer' in string:
                            peers = string.split(':')[1]
                            
                    currentSlot = headSlot - distance
                    
                    # get the time
                    logTime = line.split(' INFO')[0]
                    timeRaw = datetime.strptime(logTime, '%b %d %H:%M:%S.%f')
                    timeSecs = timeRaw.timestamp()
                
                row = [float((timeSecs - simulationTime)/(60*60)), int(currentSlot)/1000, peers]
                csvwriter.writerow(row)
        
    print("Lighthouse CSV Done")

main()
