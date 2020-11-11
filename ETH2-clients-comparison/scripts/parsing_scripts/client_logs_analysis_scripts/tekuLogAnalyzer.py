import sys
import re
#from datetime import datetime
from datetime import datetime
import matplotlib.dates 
from pathlib import Path
import csv


def main ():
    simulationTime = 0
    prevRawTime = 0
    year = 0
    month = 0
    auxDay = 0
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
                firstSlice = line.split(' main ')
                logTime = firstSlice[0]
                timeRaw = datetime.strptime(logTime,'%Y-%m-%d %H:%M:%S,%f')
                auxDay = timeRaw.day
                month = timeRaw.month
                year = timeRaw.year
                timeSecs = timeRaw.timestamp()
                simulationTime = timeSecs
            
            if "Sync Event" in line:
                # Get slot
                firstSlice = line.split('[')
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
                logTime = logTime.replace(' INFO  - ', '')
                timeRaw = datetime.strptime(logTime,'%H:%M:%S.%f').replace(year=year, month=month, day=auxDay)
                if prevRawTime == 0:
                    prevRawTime = timeRaw
                if timeRaw.timestamp() < prevRawTime.timestamp():
                    auxDay = auxDay + 1
                    timeRaw = timeRaw.replace(day=auxDay)
                timeSecs = timeRaw.timestamp()
                prevRawTime = timeRaw    
                
                row = [float((timeSecs - simulationTime)/(60*60)), int(currentSlot)/1000, peers]
                csvwriter.writerow(row)
        
    print("Teku CSV Done")

main()
