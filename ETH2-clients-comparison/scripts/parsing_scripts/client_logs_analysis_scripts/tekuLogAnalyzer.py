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

    print("Opening Teku File")
    with open(logFile) as f:
        logs = f.readlines()
    
    print("Opening Teku CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        csvwriter.writerow(["Time (hours)", "Current Slot", "Peers Connected"])
        
        # Iterate through the lines
        for line in logs:
             # remove whitespace characters like `\n` at the end of each line
            line.strip()
            # get the starting time from the beginning
            if simulationTime == 0:
                # get the time
                firstSlice = line.split(' | ')
                logTime = firstSlice[0]
                logTime = logTime.replace('+01:00', '')
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S.%f')
                timeSecs = timeRaw.timestamp()
                simulationTime = timeSecs
            
            if "Sync Event" in line:
                # Get slot
                firstSlice = line.split(' | ')
                for slices in firstSlice:
                    sslices = slices.split(',')
                    for string in sslices:
                        if 'Head slot' in string:
                            slot = string.split(' ')
                            slot[3] = slot[3].replace(',', '')
                            currentSlot = int(slot[3])
                        if 'Connected peers' in string:
                            aux = string.split(':')[1]
                            number = aux.replace('\x1b[0m\n', '')
                            number = number.replace(' ', '')
                            peers = int(number)
                
                
                # get the time
                logTime = firstSlice[0]
                logTime = logTime.replace('+01:00', '')
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S.%f')
                timeSecs = timeRaw.timestamp()
                #if simulationTime == 0:
                #   simulationTime = timeSecs
                
                row = [float((timeSecs - simulationTime)/(60*60)), currentSlot, peers]
                csvwriter.writerow(row)
        
    print("Teku CSV Done")

main()
