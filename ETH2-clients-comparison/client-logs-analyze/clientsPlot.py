import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main ():
    simulationTime = 0
    lightCsv = sys.argv[1]
    tekuCsv = sys.argv[2]

    lighthouse_syncronization = pd.read_csv(lightCsv)
   
    teku_syncronization = pd.read_csv(tekuCsv)
   
    ax = lighthouse_syncronization.plot(figsize=(20,10), x='Time (min)', y='Current Slot', label='Lighthouse')
    teku_syncronization.plot(ax=ax, x='Time (min)', y='Current Slot', label='teku')
    #ax.plot()
    plt.xlabel("Time of syncing (minutes)")
    plt.ylabel("Last synced slot")
    plt.title("Synchronization State on the Clients Starting From Empty DB")
    plt.legend()
    plt.show()
    
    print("Finishing. Ciao!")

main()
