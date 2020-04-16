# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 14:42:23 2020

@author: abric
"""

# =============================================================================
# I use this .py to generate an example of the data which can be collected
# =============================================================================

import numpy as np 
import matplotlib.pyplot as plt 


#%% Function to simulate the things

def simulate_generated_signals(noise_amplitude, numberOfPointsPerSecond, events):
    """
    Returns a simulation of what a signal can be. 
    The array even must contain event at every second.
    """
    
    data_noise = []
    data_signal = []
    time = []
    t0 = 0
    
    for event in events: 
        noise = np.random.normal(0, noise_amplitude, numberOfPointsPerSecond)
        signal = event * np.ones((numberOfPointsPerSecond, 1))
        t = np.linspace(t0, t0+1, numberOfPointsPerSecond)
        
        data_noise.append(noise)
        data_signal.append(signal)
        time.append(t)
        t0 = t0 + 1 
        
    # Process the data to plot it 
    data_noise = np.array(data_noise).ravel()
    data_signal = np.array(data_signal).ravel()
    time = np.array(time).ravel()
    data = data_noise + data_signal
    
    return time, data

#%% 

events = [0,0,0,1,0,0,1,1,1,0,0,0]

#%% 

noise_amplitude = 0.01
numberOfPointsPerSecond = 10
time, data = simulate_generated_signals(noise_amplitude, numberOfPointsPerSecond, events)

to_save = np.array([time, data])
np.savetxt('signals/signal_10pointsPerSecond.csv',to_save,delimiter=",")

fig, ax = plt.subplots()
ax.plot(time, data)
ax.set_title('Generated signal with noise and touching events')
fig.savefig('signals/signalGraph_10pointsPerSecond')

