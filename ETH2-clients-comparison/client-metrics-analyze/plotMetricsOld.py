import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use( 'tkagg' )
import json
import matplotlib.dates as dates
from datetime import datetime

#inputFile = "/home/lfrances/luca/monitorProcess/data/tekuData/tekuMetrics_0.txt"

def iterateInputFile(inputFile):
    with open(inputFile) as f:
         next(f)
         next(f)
         next(f)
         next(f)
         next(f)
         lines = f.readlines()
         clientValues = {}
         print("First line" ,lines[0])
         print("number of items in teku-metrics:", len(lines))
         for line in lines : 
             print(line)
             if 'Something went wrong\n' in line:
                 continue
             if 'Error' in line:
                 continue
             
             parameters=line.split(" , ")
            
                    #print(parameters)
                    #print(parameters[0])
                    #print(parameters[1])
                    #print(parameters[2])
                    #print(parameters[3])
                    #print(parameters[4])
                    #print(parameters[5])
             timestamp= parameters[0]
             print(parameters)
             values = [float(parameters[1]), float(parameters[2]), float(parameters[3]), float(parameters[4]), float(parameters[5].replace('\n', ''))]
             clientValues[timestamp] = values
    return clientValues

dictionaryTeku = iterateInputFile("/home/lfrances/luca/monitorProcess/data/tekuData/tekuMetrics4.txt")
dictionaryLighthouse = iterateInputFile("/home/lfrances/luca/monitorProcess/data/lighthouseData/light-metrics.txt")

#print("this is teku", dictionaryTeku)
def generateArrayFromDictTeku(dictionary, arg):
    arrayParam = [[],[]]

    for item in dictionary:
        dateTimeObj = datetime.strptime(item, '%Y-%m-%d %H:%M:%S.%f')
        date = matplotlib.dates.date2num(dateTimeObj)
        
        arrayParam[0].append(date)
        arrayParam[1].append(dictionary[item][arg])
    
    return arrayParam

def generateArrayFromDictLight(dictionary, arg):
    arrayParam = [[],[]]

    for item in dictionary:
        
        dateTimeObj = datetime.strptime("2020 " + item, '%Y %B %d %H:%M:%S:%f')
        date = matplotlib.dates.date2num(dateTimeObj)
        
        arrayParam[0].append(date)
        arrayParam[1].append(dictionary[item][arg])
    
    return arrayParam

#tekuTime = dictionaryTeku[clientValues[timestamp]]
tekuMEM = generateArrayFromDictTeku(dictionaryTeku, 0)
tekuCPU = generateArrayFromDictTeku(dictionaryTeku, 1)
tekuNETOUT = generateArrayFromDictTeku(dictionaryTeku, 2)
tekuNETIN = generateArrayFromDictTeku(dictionaryTeku, 3)
tekuDISK = generateArrayFromDictTeku(dictionaryTeku, 4)



lighthouseMEM = generateArrayFromDictLight(dictionaryLighthouse ,0)
lighthouseCPU = generateArrayFromDictLight(dictionaryLighthouse ,1)
lighthouseNETOUT = generateArrayFromDictLight(dictionaryLighthouse ,2)
lighthouseNETIN = generateArrayFromDictLight(dictionaryLighthouse ,3)
lighthouseDISK = generateArrayFromDictLight(dictionaryLighthouse ,4)

# y = [line.split()[1] for line in lines
#print("timestamp of CLient values" , clientValues[timestamp])
#print(dictionaryTeku)
print("test")
#print(dictionaryTeku[timestamp][1])
#print(lighthouseMEM)

#####datetimeObj = datetime.strptime('tekuTime', '%Y-%m-%dT %H::%M::%S.%f')
####dates = matplotlib.dates.date2num(dateTimeObj)
####plt.plot(dates, tekuMEM)

#plt.plot(lightCPU)
#plt.plot(lightNETOUT)
#plt.plot(lightNETIN)
#plt.plot(lightDISK)

#plt.plot(tekuMEM[0], tekuMEM[1])
matplotlib.pyplot.plot_date(tekuMEM[0], tekuMEM[1], label="Teku")
matplotlib.pyplot.plot_date(lighthouseMEM[0], lighthouseMEM[1], label="Lighthouse")
plt.title('MEMORY CONSUMPTION')
plt.xlabel('TIME (Month-Day-Hour)')
plt.ylabel('MEGABYTES')
plt.legend()
#axes.plot(x,x**2, color='purple', linewidth=10)
plt.show()

matplotlib.pyplot.plot_date(tekuCPU[0], tekuCPU[1], label="Teku")
matplotlib.pyplot.plot_date(lighthouseCPU[0], lighthouseCPU[1], label="Lighthouse")
plt.title('CPU')
plt.xlabel('TIME (Month-Day-Hour)')
plt.ylabel('%')
plt.legend()
#axes.plot(x,x**2, color='purple', linewidth=10)
plt.show()

matplotlib.pyplot.plot_date(tekuNETOUT[0], tekuNETOUT[1], label="Teku")
matplotlib.pyplot.plot_date(lighthouseNETOUT[0], lighthouseNETOUT[1], label="Lighthouse")
plt.title('NETOUT')
plt.xlabel('TIME (Month-Day-Hour)')
plt.ylabel('MEGABYTES')
plt.legend()
#axes.plot(x,x**2, color='purple', linewidth=10)
plt.show()

matplotlib.pyplot.plot_date(tekuNETIN[0], tekuNETIN[1], label="Teku")
matplotlib.pyplot.plot_date(lighthouseNETIN[0], lighthouseNETIN[1], label="Lighthouse")
plt.title('NETIN')
plt.xlabel('TIME (Month-Day-Hour)')
plt.ylabel('MEGABYTES')
plt.legend()
#axes.plot(x,x**2, color='purple', linewidth=10)
plt.show()

matplotlib.pyplot.plot_date(tekuDISK[0], tekuDISK[1], label="Teku")
matplotlib.pyplot.plot_date(lighthouseDISK[0], lighthouseDISK[1], label="Lighthouse")
plt.title('DISKUSAGE')
plt.xlabel('TIME (Month-Day-Hour)')
plt.ylabel('MEGABYTES')
plt.legend()
#axes.plot(x,x**2, color='purple', linewidth=10)
plt.show()
