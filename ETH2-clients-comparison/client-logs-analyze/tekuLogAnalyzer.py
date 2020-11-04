import sys
import re
#from datetime import datetime
from datetime import datetime
import matplotlib.dates 
import csv


def main ():
    simulationTime = 1604337471
    logFile = sys.argv[1]
    csvFile = sys.argv[2]

    print("Opening File")
    with open(logFile) as f:
        logs = f.readlines()
    
    print("Opening CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        csvwriter.writerow(["Time (min)", "Current Slot"])
        
        # Iterate through the lines
        for line in logs:
             # remove whitespace characters like `\n` at the end of each line
            line.strip()
            if "Head slot" in line:
                
                # Get slot
                firstSlice = line.split(' | ')
                for string in firstSlice:
                    if 'slot' in string:
                        slices = string.split(' ')
                        slices[9] = slices[9].replace(',', '')
                        currentSlot = int(slices[9])
                
                
                # get the time
                logTime = firstSlice[0]
                logTime = logTime.replace('+01:00', '')
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S.%f')
                timeSecs = timeRaw.timestamp()
                #if simulationTime == 0:
                #   simulationTime = timeSecs
                
                row = [float((timeSecs - simulationTime)/60), currentSlot]
                csvwriter.writerow(row)
        
    print("Finishing. Ciao!")

main()
