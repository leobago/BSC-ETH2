import sys
import re

import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import csv
import matplotlib.pyplot as plt
import numpy as np

def main():
	logFile = Path(__file__).parent / sys.argv[1]
	outFolder = Path(__file__).parent / sys.argv[2]
	metricsFile = Path(__file__).parent / sys.argv[3]
	csvFile = Path(__file__).parent / sys.argv[4]
	

	# Local Variable
	simulationTime = 0

	# Open the log file to read the lines
	lf = open(logFile, 'r')
	lines = lf.readlines()
	lf.close()

	# list of events:
	events = ['Starting from known genesis state', 'Storing full state on epoch boundary', 'Received BlocksByRange Response', 'Head beacon block', 'Beacon block imported', 
	'Fork choice success', 'Chain advanced', 'Starting database pruning', 'Extra pruning information', 'Database pruning complete', 'Freezer migration started']

	# Define the variables that later will be used for the analysis
	eventTracker = {'executionTime': [], 'Event Type': []}

	lightImportedBlocksPanda = {'logTime': [], 'blockSlot': [], 'blockRoot': []}

	jsonDict = {events[0]: [], events[1]: [], events[2]: [], events[3]: [], events[4]: [], events[5]: [], events[6]: [], events[7]: [], events[8]: [], events[9]: [], events[10]: []}

	# Iterate through the lines getting the jsons and storing them on a Dict
	for line in lines:
		log = json.loads(line)

		# get the simulation time (get the time of the first log)
		if simulationTime == 0:
			simulationTime = getSecsFromDate(log['ts'])

        #if any(x in line for x in events): # Only execute this part if the log is of a type message of the event list 
            # Make time-line of all the events received
            # Might be interesting to add this only with the Event Types listed on the jsonDict 

            #eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))
            #eventTracker['Event Type'].append(log['msg'])
            
        
        # filter Json of the event type into a Dict
		if log["msg"] == events[0]:
			jsonDict[events[0]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(0)
		if log["msg"] == events[1]:
			jsonDict[events[1]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(1) 
		if log["msg"] == events[2]:
			jsonDict[events[2]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(2)  
		if log["msg"] == events[3]:
			jsonDict[events[3]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(3) 
		if log["msg"] == events[4]: # Beacon Block Imported Event
			jsonDict[events[4]].append(log)
			eventTracker['executionTime'].append((getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(4)
			lightImportedBlocksPanda['logTime'].append((getSecsFromDate(log["ts"])-simulationTime)/(60*60))
			lightImportedBlocksPanda['blockSlot'].append(int(log['block_slot'])/1000)
			lightImportedBlocksPanda['blockRoot'].append(log['block_root'])
		if log["msg"] == events[5]:
			jsonDict[events[5]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(5) 
		if log["msg"] == events[6]:
			jsonDict[events[6]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(6) 
		if log["msg"] == events[7]: 
			jsonDict[events[7]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(7) 
		if log["msg"] == events[8]:
			jsonDict[events[8]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(8) 
		if log["msg"] == events[9]:
			jsonDict[events[9]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(9) 
		if log["msg"] == events[10]:
			jsonDict[events[10]].append(log)
			eventTracker['executionTime'].append( (getSecsFromDate(log["ts"])-simulationTime)/(60*60))                                                                             
			eventTracker['Event Type'].append(10) 
	
	
	# Add the imported blocks to the event tracker
	eventTracker = addPeersSlotsToDict(eventTracker, lightImportedBlocksPanda, 'executionTime', 'logTime', 'blockSlot')
	
	# Iterate through the lines on the metrics file, parsing the metrics into a Dict
	lightMetrics = getMetricsFromFile('lighthouse', metricsFile)
	lightImportedBlocksPanda = addmetricsToDict(lightImportedBlocksPanda, lightMetrics, 'logTime', 'TIME', 'MEM','CPU', 'NETOUT', 'NETIN', 'DISK')

	# Once the iteration is over
	# We generate the panda for the Event tracker
	# TODO: -Generate a different template from the given event
	#       -we can save both of the files and make a test ploting
	lightEventPanda = pd.DataFrame(data = eventTracker, columns = ['executionTime', 'Event Type', 'blockSlot'])
	print('Event Panda', lightEventPanda)
	# generate panda from the metrics and the block importation
	lightMetricsPanda = pd.DataFrame(data = lightImportedBlocksPanda, columns = ['logTime', 'blockSlot', 'blockRoot','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
	print('Metrics Panda', lightMetricsPanda)
	
	# Save to CSV the metrics + logs of lighthouse
	lightMetricsPanda.to_csv(csvFile)
	
	# Make trial plot from lighthouse
	plotColumn(lightEventPanda, opts={
        'figSize': (15,6),
        'figTitle': 'light-events.png',
        'outputPath': outFolder,
        'xlog': False,
        'ylog': False,
        'xMetrics': 'executionTime',
        'yMetrics': 'Event Type',
        'xLowLimit': None,
        'xUpperLimit': 2.5,
        'xRange': None,
        'yLowLimit': 0,
        'yRange': 1,
        'yUpperLimit': None,
        'title': "Lighthouse event's time-line while syncing",
        'xLabel': 'Hours of syncronization',
        'yLabel': 'Events MSG',
        'xTickLabel': None,
        'yTickLabel': events,
        'legendLabel': None,
        'titleSize': 20,
        'labelSize': 18,
        'lableColor': 'tab:black',
        'hGrids': None,
        'vGrids': None,
        'hlines': None,
        'vlines': None,
        'hlineColor': None,
        'vlineColor': 'r',
        'hlineStyle': None,
        'vlineStyle': '--',
        'marker': '.',
        'markerStyle': '.',
        'markerSize': 1.2,
        'lengendPosition': 1,
        'legendSize': 16,
        'tickSize': 16})

	plotColumn(lightEventPanda, opts={
        'figSize': (15,6),
        'figTitle': 'light-events-zoomed.png',
        'outputPath': outFolder,
        'xlog': False,
        'ylog': False,
        'xMetrics': 'executionTime',
        'yMetrics': 'Event Type',
        'xLowLimit': 0.70,
        'xUpperLimit': 1.05,
        'xRange': 0.05,
        'yLowLimit': 0,
        'yRange': 1,
        'yUpperLimit': None,
        'title': "Lighthouse event's time-line while syncing zoomed",
        'xLabel': 'Hours of syncronization',
        'yLabel': 'Events MSG',
        'xTickLabel': None,
        'yTickLabel': events,
        'legendLabel': None,
        'titleSize': 20,
        'labelSize': 18,
        'lableColor': 'tab:black',
        'hGrids': None,
        'vGrids': None,
        'hlines': None,
        'vlines': None,
        'hlineColor': None,
        'vlineColor': 'r',
        'hlineStyle': None,
        'vlineStyle': '--',
        'marker': '.',
        'markerStyle': '.',
        'markerSize': 1.2,
        'lengendPosition': 1,
        'legendSize': 16,
        'tickSize': 16})
        
	plotColumn(lightEventPanda, opts={
        'figSize': (15,6),
        'figTitle': 'light-events-on-slot.png',
        'outputPath': outFolder,
        'xlog': False,
        'ylog': False,
        'xMetrics': 'blockSlot',
        'yMetrics': 'Event Type',
        'xLowLimit': 0,
        'xUpperLimit': 240,
        'xRange': 25,
        'yLowLimit': 0,
        'yRange': 1,
        'yUpperLimit': None,
        'title': "Lighthouse event's time-line while syncing",
        'xLabel': 'Last synced Slot (thousands)',
        'yLabel': 'Events MSG',
        'xTickLabel': None,
        'yTickLabel': events,
        'legendLabel': None,
        'titleSize': 20,
        'labelSize': 18,
        'lableColor': 'tab:black',
        'hGrids': False,
        'vGrids': True,
        'hlines': None,
        'vlines': (73.248, 117.6),
        'hlineColor': None,
        'vlineColor': 'r',
        'hlineStyle': None,
        'vlineStyle': '--',
        'marker': '.',
        'markerStyle': '.',
        'markerSize': 1.2,
        'lengendPosition': 1,
        'legendSize': 16,
        'tickSize': 16})
        
	plotColumn(lightEventPanda, opts={
		'figSize': (15,6),
		'figTitle': 'light-events-on-slot-zoomed.png',
		'outputPath': outFolder,
		'xlog': False,
		'ylog': False,
		'xMetrics': 'blockSlot',
		'yMetrics': 'Event Type',
		'xLowLimit': 65,
		'xUpperLimit': 125,
		'xRange': 10,
		'yLowLimit': 0,
		'yRange': 1,
		'yUpperLimit': None,
		'title': "Lighthouse event's time-line while syncing",
		'xLabel': 'Last synced Slot (thousands)',
		'yLabel': 'Events MSG',
		'xTickLabel': None,
		'yTickLabel': events,
		'legendLabel': None,
		'titleSize': 20,
		'labelSize': 18,
		'lableColor': 'tab:black',
		'hGrids': False,
		'vGrids': True,
		'hlines': None,
		'vlines': (73.248, 117.6),
		'hlineColor': None,
		'vlineColor': 'r',
		'hlineStyle': None,
		'vlineStyle': '--',
		'marker': '.',
		'markerStyle': '.',
		'markerSize': 1.2,
		'lengendPosition': 1,
		'legendSize': 16,
		'tickSize': 16})
        	
	plotColumn(lightMetricsPanda, opts={
        'figSize': (15,6),
        'figTitle': 'light-Disk-on-slot-zoomed.png',
        'outputPath': outFolder,
        'xlog': False,
        'ylog': False,
        'xMetrics': 'blockSlot',
        'yMetrics': 'DISK',
        'xLowLimit': None,
        'xUpperLimit': None,
        'xRange': 20.000,
        'yLowLimit': 0,
        'yRange': None,
        'yUpperLimit': None,
        'title': "Lighthouse Disk Usage while syncing",
        'xLabel': 'Last synced Slot (thousands)',
        'yLabel': 'Disk Usage (GB)',
        'xTickLabel': None,
        'yTickLabel': None,
        'legendLabel': None,
        'titleSize': 20,
        'labelSize': 18,
        'lableColor': 'tab:black',
        'hGrids': False,
        'vGrids': True,
        'hlines': None,
        'vlines': (73.248, 117.600),
        'hlineColor': None,
        'vlineColor': 'r',
        'hlineStyle': None,
        'vlineStyle': '--',
        'marker': '.',
        'markerStyle': '.',
        'markerSize': 1.2,
        'lengendPosition': 1,
        'legendSize': 16,
        'tickSize': 16})
        
def getMetricsFromFile(clientType, inputFile):
    startingTime = 0
    startingNetOut = 0
    startingNetIn = 0
    
    # Lodestar Bias removed
    prevDiskValue = 0
    prevDiskBiasValue = 0
    totalBiasDiff = 0
    totalDiskIncrease = 0
    auxCount = 0
    averageDiskIncrease = 0
    biasTimeStart = 1604871411 # 2020-Nov-08 22:36:51
    biasTimeFinish = 1604872160 # 2020-Nov-0 8 22:49:20
    #biasSize = 9343.5 # Size of the folder Downloaded (MB)
    
    # Degfine the dictionary that later will be the the panda
    clientMetrics = {'TIME': [], 'MEM': [], 'CPU': [], 'NETOUT': [], 'NETIN': [], 'DISK': []}
    
    f = open(inputFile, 'r')
    lines = f.readlines()
    # close the file
    f.close()
    
    # Iterate through the lines on the file
    for line in lines:
        if ("Something went wrong" in line) or ("Error" in line) or ('Pid' in line) or ('Monitoring' in line) or ('The size' in line) or ('TIME' in line) or('Welcome' in line) or('.eth2' in line):
            continue
        parameters = line.split(" , ")
        
        # Get the date in secs from the lighthouse format
        if clientType == 'lighthouse':
            timeRaw = datetime.strptime(parameters[0], '%B %d %H:%M:%S:%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the teku format
        if clientType == 'teku':
            parameters[0] = parameters[0].replace('+01:00', '')
            timeRaw = datetime.strptime(parameters[0], '%Y-%m-%d %H:%M:%S.%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the nimbus format
        if clientType == 'nimbus':
            timeRaw = datetime.strptime(parameters[0], '%Y-%m-%d %H:%M:%S.%f')
            timeSecs = timeRaw.timestamp()
        # Get the date in secs from the nimbus format
        if clientType == 'prysm':
            timeRaw = datetime.strptime(parameters[0], '%Y-%b-%d %H:%M:%S')
            timeSecs =timeRaw.timestamp()
        # Get the date in secs from the lodestar format
        if clientType == 'lodestar':
            timeRaw = datetime.strptime(parameters[0], '%Y-%b-%d %H:%M:%S')
            timeSecs =timeRaw.timestamp()
            
        # get the starting point
        if startingTime == 0:
            startingTime = timeSecs
            startingNetOut = float(parameters[3])
            startingNetIn = float(parameters[4])
        
        
        timeMins = (timeSecs - startingTime)/60 # We convert them to minutes
        netOut = (float(parameters[3]) - startingNetOut)
        netIn = (float(parameters[4]) - startingNetIn)
        
        # Lodestar Bias Remove
        if clientType == 'lodestar':
            if auxCount == 0:
                startingTimeOfLodestar = timeSecs
            if timeSecs < biasTimeStart:
                auxCount = auxCount + 1
                totalDiskIncrease = totalDiskIncrease + (netOut - prevDiskValue)
                #print('BaseTime:', startingTimeOfLodestar)
                #print('startTime:', biasTimeStart, 'currentTime:', timeSecs)
                #print('totalDiskIncrease:', totalDiskIncrease)
                #print ('CNT:', auxCount)
                netOut = totalDiskIncrease
                prevDiskValue = netOut
                prevDiskBiasValue = prevDiskValue
            if timeSecs >= biasTimeStart and timeSecs <= biasTimeFinish:
                averageDiskIncrease =  totalDiskIncrease / auxCount 
                totalBiasDiff = (netOut - totalDiskIncrease)
                #print('net', netOut,'prev',prevDiskBiasValue)
                netOut = prevDiskBiasValue + averageDiskIncrease
                #print(netOut)
                #print('Average:', averageDiskIncrease)
                #print('TotalBias:', totalBiasDiff)
                prevDiskBiasValue = netOut
            if timeSecs > biasTimeFinish:
                #print('Prev:', prevDiskBiasValue)
                netOut = netOut - totalBiasDiff
                print('net:', netOut)
                
        
        # Append values to the clientMetrics dict
        clientMetrics['TIME'].append(timeMins/60)
        clientMetrics['MEM'].append(float(parameters[1])/1000)
        clientMetrics['CPU'].append(float(parameters[2]))
        clientMetrics['NETOUT'].append(netOut/1000)
        clientMetrics['NETIN'].append(netIn/1000)
        clientMetrics['DISK'].append((float(parameters[5].replace('\n', '')))/1000)
    
    #metricsPanda = pd.DataFrame(data = clientMetrics, columns = ['TIME','MEM','CPU', 'NETOUT', 'NETIN', 'DISK'])
    #return metricsPanda
    return clientMetrics
        
        
# Function that will add the slot on the head slot of time where the logs where received 
def addPeersSlotsToDict(dict1, dict2, time1, time2, column):       
	dict2index = 0                                                             
	columnarray = []                                                           
	for idx, val in enumerate(dict1[time1]):                                        
		if idx == 0:                                                          
			columnarray.append(dict2[column][dict2index])           
				                                                
		elif dict1[time1][idx] < dict2[time2][dict2index]:
			columnarray.append(int(dict2[column][dict2index]))
		else:                                                                   
			try:                                                                
				dict2index = dict2index + 1
				columnarray.append(int(dict2[column][dict2index]))       
			except:                                                           
				dict2index = dict2index - 1                                   
				columnarray.append(int(dict2[column][dict2index]))
	                                           
	dict1[column] = columnarray                 
	return dict1

# Function that will add the slot on the head slot of time where the logs where received 
def addmetricsToDict(dict1, dict2, time1, time2, column1, column2, column3, column4, column5):       
	dict2index = 0                                                             
	column1array = []
	column2array = []
	column3array = []
	column4array = []
	column5array = []
	                                                         
	for idx, val in enumerate(dict1[time1]):                                        
		if idx == 0:                                                          
			column1array.append(dict2[column1][dict2index])
			column2array.append(dict2[column2][dict2index])
			column3array.append(dict2[column3][dict2index])
			column4array.append(dict2[column4][dict2index])
			column5array.append(dict2[column5][dict2index])         
				                                                
		elif dict1[time1][idx] < dict2[time2][dict2index]:
			column1array.append(dict2[column1][dict2index])
			column2array.append(dict2[column2][dict2index])
			column3array.append(dict2[column3][dict2index])
			column4array.append(dict2[column4][dict2index])
			column5array.append(dict2[column5][dict2index]) 
		else:                                                                   
			try:                                                                
				dict2index = dict2index + 1
				column1array.append(dict2[column1][dict2index])
				column2array.append(dict2[column2][dict2index])
				column3array.append(dict2[column3][dict2index])
				column4array.append(dict2[column4][dict2index])
				column5array.append(dict2[column5][dict2index])        
			except:                                                           
				dict2index = dict2index - 1                                   
				column1array.append(dict2[column1][dict2index])
				column2array.append(dict2[column2][dict2index])
				column3array.append(dict2[column3][dict2index])
				column4array.append(dict2[column4][dict2index])
				column5array.append(dict2[column5][dict2index]) 
	                                           
	dict1[column1] = column1array
	dict1[column2] = column2array
	dict1[column3] = column3array
	dict1[column4] = column4array
	dict1[column5] = column5array                 
	return dict1

# Returns the time in seconds from the given date string          
def getSecsFromDate(date):
    date = date.replace('T', ' ')
    date = date.replace('+01:00', '')
    date = date[:-3]
    timeRaw = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    timeRaw = timeRaw.replace(hour=timeRaw.hour+1)
    return timeRaw.timestamp()


def plotColumn(panda, opts):

	outputFile = str(opts['outputPath']) + '/' + opts['figTitle']
	print('printing image', opts['figTitle'], 'on', outputFile)

	fig = plt.figure(figsize = opts['figSize'])
	ax = fig.add_subplot(111)

	panda.plot(ax=ax, logx=opts['xlog'], logy=opts['ylog'], x=opts['xMetrics'], y=opts['yMetrics'], style=opts['markerStyle'], marker=opts['marker'], markersize=opts['markerSize'], label=opts['legendLabel'])

	ax.set_ylabel(opts['yLabel'], fontsize=opts['labelSize'])
	ax.set_xlabel(opts['xLabel'], fontsize=opts['labelSize'])

	ax.tick_params(axis='both', labelsize=opts['tickSize'])

	# Check if the legend was enabled
	if opts['legendLabel'] != None:
	# Adding opts['legendSize'] as markerscale might not be the best option, try and see how it looks
	# if it doesn't look nice, change by adding a new flag 
		ax.legend(markerscale=opts['legendSize'], loc=opts['legendPosition'], ncol=ncol, prop={'size':opts['legendSize']})
	else:
		ax.get_legend().remove()

	# Set/No the grids if specified
	if opts['hGrids'] != False:
		ax.grid(which='major', axis='y', linestyle='--')
	if opts['vGrids'] != False:
		ax.grid(which='major', axis='x', linestyle='--')

	# Check if any limit was set for the x axis 
	if opts['xLowLimit'] != None and opts['xUpperLimit'] != None: # For X axis
		print("Both X limits set")
		ax.xaxis.set_ticks(np.arange(opts['xLowLimit'], opts['xUpperLimit'], opts['xRange']))
		ax.set_xlim(left=opts['xLowLimit'], right=opts['xUpperLimit'])
	elif opts['xLowLimit'] != None:
		print("Only xLow limit set")
		ax.xaxis.set_ticks(np.arange(opts['xLowLimit'], panda[opts['xMetrics']].iloc[-1]+1, opts['xRange']))
		ax.set_xlim(left=opts['xLowLimit'], right=panda[opts['xMetrics']].iloc[-1]+1)
	elif opts['xUpperLimit'] != None:
		print("Only xUpper limit set")
		ax.xaxis.set_ticks(np.arange(0, opts['xUpperLimit'], opts['xRange']))
		ax.set_xlim(left=0, right=opts['xUpperLimit'])
	else:
		print("Non xLimit set") 
		ax.xaxis.set_ticks(np.arange(0, panda[opts['xMetrics']].iloc[-1]+1, opts['xRange']))
		ax.set_xlim(left=0, right=panda[opts['xMetrics']].iloc[-1]+1)

	# Check if any limit was set for y axis 
	#if opts['yLowLimit'] != None and opts['yUpperLimit'] != None: # For X axis
	#    print("Both Y limits set")
	#    ax.yaxis.set_ticks(np.arange(opts['yLowLimit'], opts['yUpperLimit'], opts['yRange']))
	#    ax.set_ylim(bottom=opts['yLowLimit'], top=opts['yUpperLimit'])
	#elif opts['yLowLimit'] != None:
	#    print("Only yLow limit set")
	#    #ax.yaxis.set_ticks(np.arange(opts['yLowLimit'], panda[opts['yMetrics']].iloc[-1]+1, opts['yRange']))
	#    ax.set_ylim(bottom=opts['yLowLimit'], top=panda[opts['yMetrics']].iloc[-1]+1)
	#elif opts['yUpperLimit'] != None:
	#    print("Only yUpper limit set")
	#    #ax.yaxis.set_ticks(np.arange(0, opts['yUpperLimit'], opts['yRange']))
	#    ax.set_ylim(bottom=0, top=opts['yUpperLimit'])
	#else:
	#    print("Non yLimit set") 
	#    ax.yaxis.set_ticks(np.arange(0, panda[opts['yMetrics']].iloc[-1]+1, opts['yRange']))
	#    ax.set_ylim(bottom=0, top=panda[opts['yMetrics']].iloc[-1]+1)

	if opts['yLowLimit'] != None:
		ax.set_ylim(bottom=opts['yLowLimit'])
	if opts['yUpperLimit'] != None:
		ax.set_ylim(top=opts['yUpperLimit'])
	if opts['yRange'] != None:
		ax.yaxis.set_ticks(np.arange(opts['yLowLimit'], panda[opts['yMetrics']].iloc[-1]+1, opts['yRange']))

	# Set horizontal and vertical lines if needed
	if opts['hlines'] != None:
		for item in opts['hlines']:
			print('ploting h line on', item)
			plt.axhline(y=item, color=opts['hlineColor'], linestyle=opts['hlineStyle'])
	if opts['vlines'] != None:
		for item in opts['vlines']:
			print('ploting v line on', item)
			plt.axvline(x=item, color=opts['vlineColor'], linestyle=opts['vlineStyle'])

	# Set the ticks of the labels if specified
	if opts['xTickLabel'] != None:
		ax.set_xticklabels(opts['xTickLabel'])

	if opts['yTickLabel'] != None:
		ax.set_yticklabels(opts['yTickLabel'])


	plt.title(opts['title'], fontsize=opts['titleSize'])
	plt.tight_layout()
	plt.savefig(outputFile)
	plt.show()



main()
