# Copyright (C) 2022 Analog Devices, Inc.
#
# SPDX short identifier: ADIBSD


import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

import adi

device_name = "ad4000"
vref = 5.0  # Manually entered, consult eval board manual

# Optionally pass URI as command line argument,
# else use default context manager search
my_uri = sys.argv[1] if len(sys.argv) >= 2 else "ip:analog.local"
print("uri: " + str(my_uri))

my_adc = adi.ad4000(uri=my_uri)
my_adc.rx_buffer_size = 4096
my_adc.channel[0].sampling_frequency = 1100000

print("Sample Rate: ", my_adc.channel[0].sampling_frequency)

data = my_adc.rx()

# Debug: Check what type of data we received
print("Data type:", type(data))
print("Data dtype:", data.dtype if hasattr(data, 'dtype') else 'No dtype')
print("Data shape:", data.shape if hasattr(data, 'shape') else len(data))
print("First few elements:", data[:5] if hasattr(data, 'shape') else [ch[:5] for ch in data[:2]])

# Handle multi-channel data from AD4000
if isinstance(data, list):
    print(f"Multi-channel data detected: {len(data)} channels")
    # Use first channel for analysis
    data = data[0]
    print(f"Using channel 0 - shape: {data.shape}, dtype: {data.dtype}")

# Handle complex data or convert to real values
if np.iscomplexobj(data):
    # If data is complex, take the real part or magnitude
    data = np.abs(data)
elif hasattr(data, 'dtype') and 'complex' in str(data.dtype):
    data = np.abs(data)

# Ensure data is a numpy array of real numbers
data = np.array(data, dtype=np.float64)

x = np.arange(0, len(data))
voltage = data * 2.0 * vref / (2 ** 20)
voltage2 = my_adc.channel[0].scale * data
print("Scale: ", voltage)
dc = np.average(voltage)  # Extract DC component
ac = voltage - dc  # Extract AC component

plt.figure(1)
plt.clf()
plt.title("AD4020 Time Domain Data")
plt.plot(x, voltage2)
plt.ylim(0, 5000)
plt.xlabel("Data Point")
plt.ylabel("mv")
plt.show()

f, Pxx_spec = signal.periodogram(
    ac, my_adc.channel[0].sampling_frequency, window="flattop", scaling="spectrum"
)
Pxx_abs = np.sqrt(Pxx_spec)

plt.figure(2)
plt.clf()
plt.title("AD4020 Spectrum (Volts absolute)")
plt.semilogy(f, Pxx_abs)
plt.ylim([1e-6, 4])
plt.xlabel("frequency [Hz]")
plt.ylabel("Voltage (V)")
plt.draw()
plt.show()

del my_adc
