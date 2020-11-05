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

    print("Opening Nimbus File")
    with open(logFile) as f:
        logs = f.readlines()
    
    print("Opening Nimbus CSV File")
    with open(csvFile, 'w') as csvf:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvf)
        csvwriter.writerow(["Time (hours)", "Current Slot"])
        
        # Iterate through the lines
        for line in logs:
             # remove whitespace characters like `\n` at the end of each line
            line.strip()
            if "Slot end" in line:
                # Get block
                firstSlice = line.split('[')
                headSlice = firstSlice[25]
                currentSlot =  headSlice.split(':')[1]

                # get the time
                logTime = firstSlice[2]
                logTime = logTime.replace('+01:00 ', '')
                logTime = logTime.split('m ')[1]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S.%f')
                timeSecs = timeRaw.timestamp()
                if simulationTime == 0:
                   simulationTime = timeSecs

                row = [float((timeSecs - simulationTime)/(60*60)), currentSlot]
                csvwriter.writerow(row)

    
    print("Nimbus CSV Done")

main()
