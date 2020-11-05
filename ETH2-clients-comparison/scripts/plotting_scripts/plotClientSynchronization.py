import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def main ():
    simulationTime = 0
    lightCsv = Path(__file__).parent / sys.argv[1]
    tekuCsv = Path(__file__).parent / sys.argv[2]
    nimbusCsv = Path(__file__).parent / sys.argv[3]
    prysmCsv = Path(__file__).parent / sys.argv[4]
    
    figuresPath = Path(__file__).parent / '../../figures/ClientSynchronization.pdf'
    
    lighthouse_syncronization = pd.read_csv(lightCsv)
    teku_syncronization = pd.read_csv(tekuCsv)
    nimbus_syncronization = pd.read_csv(nimbusCsv)
    prysm_syncronization = pd.read_csv(prysmCsv)
   
    ax = lighthouse_syncronization.plot(figsize=(20,10), x='Time (hours)', y='Current Slot', label='Lighthouse')
    teku_syncronization.plot(ax=ax, x='Time (hours)', y='Current Slot', label='Teku')
    nimbus_syncronization.plot(ax=ax, x='Time (hours)', y='Current Slot', label='Nimbus')
    prysm_syncronization.plot(ax=ax, x='Time (hours)', y='Current Slot', label='Prysm')
    ax.grid(True)
    plt.xlabel("Time of syncing (hours)")
    plt.ylabel("Last synced slot")
    plt.title("Synchronization State on the Clients Starting From Empty DB")
    plt.legend()
    plt.savefig(figuresPath)
    plt.show()
    
    
    
    print("Finishing. Ciao!")

main()
