import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main ():
    simulationTime = 0
    lightCsv = sys.argv[1]
    tekuCsv = sys.argv[2]
    nimbusCsv = sys.argv[3]
    prysmCsv = sys.argv[4]
    
    lighthouse_syncronization = pd.read_csv(lightCsv)
    teku_syncronization = pd.read_csv(tekuCsv)
    nimbus_syncronization = pd.read_csv(nimbusCsv)
    prysm_syncronization = pd.read_csv(prysmCsv)
   
    ax = lighthouse_syncronization.plot(figsize=(20,10), x='Time (min)', y='Current Slot', label='Lighthouse')
    teku_syncronization.plot(ax=ax, x='Time (min)', y='Current Slot', label='Teku')
    nimbus_syncronization.plot(ax=ax, x='Time (min)', y='Current Slot', label='Nimbus')
    prysm_syncronization.plot(ax=ax, x='Time (min)', y='Current Slot', label='Prysm')
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("Last synced slot")
    plt.title("Synchronization State on the Clients Starting From Empty DB")
    plt.legend()
    plt.show()
    
    print("Finishing. Ciao!")

main()
