import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import csv


def main():
    tekuCsv = Path(__file__).parent / sys.argv[1]
    figureFolder = Path(__file__).parent / sys.argv[2]

    print('CSV to read:', tekuCsv)
    print('Destination folder for the pictures:', figureFolder)

    # Read the csv of teku-full-logs
    tekuPanda = pd.read_csv(tekuCsv)

    
    plotColumn(tekuPanda, opts={
        'figSize': (10,6),
        'figTitle': 'cnt-slot.png',
        'outputPath': figureFolder,
        'xlog': False,
        'ylog': True,
        'xMetrics': 'slot',
        'yMetrics': 'cnt',
        'xLowLimit': 0,
        'xUpperLimit': 400000,
        'xRange': 50000,
        'yLowLimit': 0,
        'yRange': None,
        'yUpperLimit': None,
        'title': 'Amount of times that the blocks were queued/processed',
        'xLabel': 'Slots on the Beacon Chain',
        'yLabel': 'Number of times queued/processed',
        'legendLabel': None,
        'titleSize': 20,
        'labelSize': 18,
        'lableColor': 'tab:orange',
        'hGrids': True,
        'vGrids': True,
        'marker': '.',
        'markerStyle': None,
        'markerSize': 0.5,
        'lengendPosition': 1,
        'legendSize': 16,
        'tickSize': 16})


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
    
    # temp
    print(type(panda[opts['xMetrics']][0]))
    print(type(panda[opts['yMetrics']].iloc[-1])) 

    # Check if any limit was set for the x and y axis 
    #if opts['xLowLimit'] != None and opts['xUpperLimit'] != None: # For X axis
    #    print("Both X limits set")
    #    ax.xaxis.set_ticks(np.arange(opts['xLowLimit'], opts['xUpperLimit'], opts['xRange']))
    #elif opts['xLowLimit'] != None:
    #    print("Only xLow limit set")
    #    ax.xaxis.set_ticks(np.arange(opts['xLowLimit'], panda[opts['xMetrics']].iloc[-1]+1, opts['xRange']))
    #elif opts['xUpperLimit'] != None:
    #    print("Only xUpper limit set")
    #    ax.xaxis.set_ticks(np.arange(0, opts['xUpperLimit'], opts['xRange']))
    #else:
    #    print("Non xLimit set") 
    #    ax.xaxis.set_ticks(np.arange(0, panda[opts['xMetrics']].iloc[-1]+1, opts['xRange']))
    #ax.xaxis.set_ticks(np.arange(opts['xLowLimit'], opts['xUpperLimit'], opts['xRange']))


    plt.title(opts['title'], fontsize=opts['titleSize'])
    plt.tight_layout()
    plt.savefig(outputFile)
    plt.show()

main()
