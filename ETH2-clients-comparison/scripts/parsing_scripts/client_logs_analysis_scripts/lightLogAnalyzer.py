import sys
import re
#from datetime import datetime
from datetime import datetime
import csv


def main ():
    headSlot = 0
    CurrentSlot = 0
    simulationTime = 0
    logFile = sys.argv[1]
    csvFile = sys.argv[2]

    with open(logFile) as f:
        logs = f.readlines()
        

    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        
        csvwriter.writerow(["Time (min)", "Current Slot"])
        
        # Iterate through the lines
        for line in logs:
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
                    # get the time
                    logTime = line.split(' INFO')[0]
                    timeRaw = datetime.strptime(logTime, '%b %d %H:%M:%S.%f')
                    timeSecs = timeRaw.timestamp()
                    headSlot = distance
                    # Assing the variables that will be added to de .csv file
                    currentSlot = headSlot - distance
                    simulationTime = timeSecs
                    
                else:
                    # Increase the HeadSlot as every 12sec we receive a syncing message
                    headSlot += 1
                    
                # Get distance
                    firstSlice = line.split(',')
                    for string in firstSlice:
                        if 'distance' in string:
                            number = string.split(' ')
                            distance = int(number[2])
                    
                    currentSlot = headSlot - distance
                    
                    # get the time
                    logTime = line.split(' INFO')[0]
                    timeRaw = datetime.strptime(logTime, '%b %d %H:%M:%S.%f')
                    timeSecs = timeRaw.timestamp()
                
                row = [(timeSecs - simulationTime)/60, currentSlot]
                csvwriter.writerow(row)
        
    print("Finishing. Ciao!")

main()