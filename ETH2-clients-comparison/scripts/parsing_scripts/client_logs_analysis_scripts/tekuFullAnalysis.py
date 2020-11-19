import sys
import re

import pandas as pd
from datetime import datetime
from pathlib import Path
import csv

# Define Global Variable 
genesisStateRoot = ''
genesisBlockRoot = ''
genesisTime = 0


def main ():
    logFile = Path(__file__).parent / sys.argv[1]
    csvFile = Path(__file__).parent / sys.argv[2]
    # slot
    # root
    # proposerIndex
    # parentRoot
    # stateRoot
    # qTime  -> queued time
    # prTime -> process response time (time when the response to the block sender? was processed)
    # srTime -> send response time (time when the response was sent to the block sender?) 
    # iTime  -> import time (time when the block was imported)
    # isTime -> import successful time (time when the block was successfully imported)
    # fpTime -> finish processing time (time when the processing of the block import was finished)
    # origTime -> original tiem when the block was proposed to the 
    tekuPanda = {'cnt': [], 'slot': [], 'root': [], 'proposerIndex': [], 'parentRoot': [], 'stateRoot': [], 'qTime': [], 
    'prTime':[], 'srTime': [], 'isTime': [], 'fpTime': [], 'origTime': [], 'currentQueue': [], 'size': []}
    
    # ---   Aux variables   ---
    simulationStartingTime = 0
    lastSeenSlot = 0
    queuedBlocks = 0
    # --- end of aux variables ---

    # Open the log file
    lf = open(logFile, 'r') 
    logs = lf.readlines()

    # first iteration through the lines of the logs
    for line in logs:
        if simulationStartingTime == 0:
            if ' | ' in line:
                timeSlice = line.split(' | ')[0]
                timeRaw = datetime.strptime(timeSlice, '%Y-%m-%d %H:%M:%S.%f+01:00')
                print(timeRaw)
                timeRaw = timeRaw.replace(hour=timeRaw.hour+1)
                print(timeRaw)
                simulationStartingTime = timeRaw.timestamp()
        
        # Initialize the Panda Info with the Genesis State/Block/Time
        # Get the genesis state root 
        if 'Genesis state root:' in line:
            genesisStateRoot = line.split(': ')[1]
        # Get the genesis block root
        if 'Genesis block root:' in line:
            genesisBlockRoot = line.split(': ')[1]
        # Get the genesis time
        if 'Genesis time:' in line:
            firstSlice = line.split(': ')[1]
            gTime = firstSlice.replace(' GMT\x1b[0m\n', '')
            rawTime = datetime.strptime(gTime, '%Y-%m-%d %H:%M:%S')
            genesisTime = rawTime.timestamp()
            
            # Once the main info from the genesis of the testnet has been readed
            # we introduce it on the panda
            includeRowInPanda(tekuPanda, 1, lastSeenSlot, genesisBlockRoot, 0, '', genesisStateRoot, [], [], [], [], [], genesisTime, queuedBlocks, 0)
            addItemOnPandaColumn(tekuPanda, lastSeenSlot, 'qTime', simulationStartingTime)
            addItemOnPandaColumn(tekuPanda, lastSeenSlot, 'prTime', simulationStartingTime)
            addItemOnPandaColumn(tekuPanda, lastSeenSlot, 'srTime', simulationStartingTime)
            addItemOnPandaColumn(tekuPanda, lastSeenSlot, 'isTime', simulationStartingTime)
            addItemOnPandaColumn(tekuPanda, lastSeenSlot, 'fpTime', simulationStartingTime)

        # Analyze the log that adds a block to the processing queue   
        if 'Queue response for processing: SignedBeaconBlock' in line:
            logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot = parseBlockDataFromLog(line) 
            # Check if the new block is the block corresponding for the next slot
            auxLastSeenSlot = lastSeenSlot
            print('Received Block', blockSlot)
            while((auxLastSeenSlot+1) < blockSlot): # If the last seen slot +1 is smaller than the blockSlot we just received, means there is/are non proposed slots in-between
                auxLastSeenSlot = auxLastSeenSlot + 1 
                includeEmptyRawInPanda(tekuPanda, auxLastSeenSlot, queuedBlocks, genesisTime)
            
            print('last seen slot:', auxLastSeenSlot, ' | incoming slot:', blockSlot)
            origTime = getOriginalTimeFromSlot(blockSlot, genesisTime)
            # Increment the queued blocks in one (the queue will be free when the block is successfully imported)
            queuedBlocks = queuedBlocks + 1
            print('Queue Size increased to:', queuedBlocks)
            # include the new block that the client just included on the queue 
            # the size of the block is still unknown (TODO: use an ETH2 client API to get the size of the blocks) 
            includeRowInPanda(tekuPanda, 1, blockSlot, blockRoot, proposerIndex, parentRoot, stateRoot, [], [], [], [], [], origTime, queuedBlocks, 0)
            # Include the logTime on the qTime and the current queue size
            addItemOnPandaColumn(tekuPanda, blockSlot, 'qTime', logTime)
            if blockSlot > lastSeenSlot:
                # Update the last seen slot to the recently added block number
                lastSeenSlot = blockSlot

        # Analyze the logs that Processes the response for the received BeaconBlock
        if 'Process response: SignedBeaconBlock' in line:
            print('New Process response')
            logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot = parseBlockDataFromLog(line)
            addItemOnPandaColumn(tekuPanda, blockSlot, 'prTime', logTime)

        # Analyze the logs that Sends response to the peer? that sent the block
        if 'Send response to response stream: SignedBeaconBlock' in line:
            print('New Send response to stream')
            logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot = parseBlockDataFromLog(line)
            addItemOnPandaColumn(tekuPanda, blockSlot, 'srTime', logTime)

        # Analyze the logs that says that the block was successfully imported
        if 'Block import result for block at' in line:
            print('New Successfully Imported Block')
            logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot = parseBlockDataFromLog(line)
            addItemOnPandaColumn(tekuPanda, blockSlot, 'isTime', logTime)

        # Analyze the logs that says that the block processing is finished
        if 'Finish processing: SignedBeaconBlock' in line:                          
            print('New Processing Finish')                            
            logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot = parseBlockDataFromLog(line)  
            queuedBlocks = queuedBlocks - 1
            addItemOnPandaColumn(tekuPanda, blockSlot, 'fpTime', logTime)
            print('Queue Size decresed to:', queuedBlocks) 

    print('All logs parsed')
    tekuMetricsPanda = pd.DataFrame(data = tekuPanda, columns = ['cnt', 'slot', 'root', 'proposerIndex', 'parentRoot', 'stateRoot', 
    'qTime', 'prTime', 'srTime', 'isTime', 'fpTime', 'origTime', 'currentQueue', 'size'])
    print('Panda Generated', tekuMetricsPanda)
    print('Finishing! Ciao :*')
    tekuMetricsPanda.to_csv(csvFile)
    lf.close()

# Modifies or Includes a date/whatever on an existent row of the panda (originaly planed to include dates/time of processing on already seen blocks)
def addItemOnPandaColumn(panda, blockSlot, column, valueToInclude):
    print('BlockSlot:', blockSlot, ' | Column:', column, 'value to include', valueToInclude)
    if panda['slot'][blockSlot] == blockSlot:
        panda[column][blockSlot].append(valueToInclude)
        print('Successfully Included!')
    else:
        print('Accessing the slot:', panda[column][blockSlot], 'instead of:', blockSlot)
        print('Block slot doesnt correspond with the panda slot')
        exit()

# returns all the info related to the block from the log (ONLY if the block includes a SignedBeaconBlock)
def parseBlockDataFromLog(logLine):
    firstSlice = logLine.split(' | ')
    # First part of the logs always gives the log-time
    timeString = firstSlice[0]
    logTime = getSecsFromDate(timeString)
    # Parse the content of the received block
    blockInfo = firstSlice[-1]
    blockInfo = blockInfo.split('{')[-1]
    blockInfo = blockInfo.split(', ')
    blockRoot = blockInfo[0].split('=')[-1]
    blockSlot = int(blockInfo[1].split('=')[-1])
    proposerIndex = int(blockInfo[2].split('=')[-1])
    parentRoot = blockInfo[3].split('=')[-1]
    stateRoot = blockInfo[4].split('=')[-1]
    
    return logTime, blockRoot, blockSlot, proposerIndex, parentRoot, stateRoot

# Returns the time in seconds from the given date string
def getSecsFromDate(date):
    timeRaw = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f+01:00')
    timeRaw = timeRaw.replace(hour=timeRaw.hour+1)
    return timeRaw.timestamp()

# Calculates the original time in seconds of when the slot was proposed
def getOriginalTimeFromSlot(slotNumber, genesisTime):
    # every slot has to be proposed after 12 seconds
    slotTime = (12 * slotNumber) + genesisTime
    return slotTime

# Funtion that includes a empty row on the panda (for when the slot is missing)
def includeEmptyRawInPanda(panda, slot, currentQueue, genesisTime):
    origSlotTime = getOriginalTimeFromSlot(slot, genesisTime)
    includeRowInPanda(panda, 0, slot, '', 0, '', '', [], [], [], [], [], origSlotTime, currentQueue, 0)
    #print('Included New Empty Slot:', slot) 

# Function that includes new raw corresponding to a new slot on the testnet on the panda
# TODO: - Change all this args to a dict array (would make it cleaner and simpler) 
def includeRowInPanda(panda, cnt, slot, root, propIndex, parent, state, qtime, prtime, srtime, istime, fptime, origtime, queuesize, size):
    try:    
        if panda['slot'][slot]: # if the received block was already on the list, just add the times       
            panda['cnt'][slot] = panda['cnt'][slot] + 1
            #panda['slot']
            panda['root'][slot] = root
            panda['proposerIndex'][slot] = propIndex
            panda['parentRoot'][slot] = parent
            panda['stateRoot'][slot] = state
            #panda['qTime'][slot].append()
            #panda['prTime']
            #panda['srTime']
            #panda['isTime']
            #panda['fpTime']
            panda['currentQueue'][slot] = queuesize
            #panda['size']
            #print('New dates added on slot:', slot, ' - ', panda['cnt'][slot])
    except: # if the received block wasn't seen before, create a new item on the list
        panda['cnt'].append(cnt)
        panda['slot'].append(slot)
        panda['root'].append(root)
        panda['proposerIndex'].append(propIndex)
        panda['parentRoot'].append(parent)
        panda['stateRoot'].append(state)
        panda['qTime'].append(qtime)
        panda['prTime'].append(prtime)
        panda['srTime'].append(srtime)
        panda['isTime'].append(istime)
        panda['fpTime'].append(fptime)
        panda['origTime'].append(origtime)
        panda['currentQueue'].append(queuesize)
        panda['size'].append(size)
        print('New Row added, slot:', slot)

main()
