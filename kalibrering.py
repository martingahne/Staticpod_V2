
#library för hårdvara
from curses import KEY_F0
import qwiic_tca9548a
import PyNAU7802
import smbus2

#library för tidtagning och sparande av data.
from pytictoc import TicToc
import numpy
import pandas
import plotly.express as px
import math



################################################################################
#här finns portarna som man vill koppla till på muxen
################################################################################
ports = [6, 2, 1, 0, 7, 5]

#skapar mux med address 0x70
mux = qwiic_tca9548a.QwiicTCA9548A(address=0x70)

#skapar bus för i2c kommunikation
bus = smbus2.SMBus(1)

#tidtagare för prestandatest
t = TicToc()

#öppnar/stänger portar på muxen
def enable_port(mux: qwiic_tca9548a.QwiicTCA9548A, leg):
    mux.enable_channels(ports[leg])

def disable_port(mux: qwiic_tca9548a.QwiicTCA9548A, leg):
    mux.disable_channels(ports[leg])

##########################################################################
#öppnar en port på muxen, skapar ett adc objekt för den porten och lägger till i listan adcs. stänger sedan porten.
##########################################################################
adcs = list()
for i in range(len(ports)):
    enable_port(mux, i)
    adc = PyNAU7802.NAU7802()
    adc.begin(bus)
    adcs += [adc]
    disable_port(mux, i)

########################################################################
#setgain säkerställer att alla adcs har samma gain.
########################################################################

for i in range(len(ports)):
    enable_port(mux, i)
    adcs[i].setGain(128)

########################################################################
#öppnar port i, läser av adc i, stänger port i. itererar över alla adc.
########################################################################
def get_scales(mux, samples):
    f = [[], [], [], [], [], []]
    t.tic()
    for i in range(samples):
        for i in range(len(ports)):
            enable_port(mux, i)

            f0 = adcs[i].getReading()
            f[i].append(f0)

            disable_port(mux, i)
    tid = t.tocvalue()*samples

    time = numpy.true_divide((numpy.arange(samples)), tid)
    return f, time

###############################################################
#användarinput vid kalibrering
###############################################################
input('kalibrering av vågen, ingen belastning')
f_noload, time = get_scales(mux, 100)
print(f_noload[4])
vikt = float(input('kalibrering av vågen, ange vikt'))
f_loaded, time = get_scales(mux, 100)

#################################################################
#beräkning av m
###############################################################
fmean_noload = []
for i in range(len(ports)):
    fmean_noload.append(numpy.mean(f_noload[i]))

print('noload m värden:')
print(fmean_noload)
m_vals = fmean_noload

################################################################
#medelvärde under load
################################################################
fmean_loaded = []
for i in range(len(ports)):
    fmean_loaded.append(numpy.mean(f_loaded[i]))

#######################################################
#beräknar k
###############################################
k_vals = []


for i in range(len(ports)):
    k = ((vikt*9.82)/(6*0.9077))/(fmean_loaded[i] - fmean_noload[i]) 
    k_vals.append(k)
print('k values:')
print(k_vals)

####################################################################
#datum till filnamn
#############################################
from datetime import datetime
now = datetime.now()
tid = now.strftime("%d/%m/%Y %H:%M:%S")
print(tid)
name = str(input('filnamn,kalibrering_datum'))

#########################################################
#sparar som csv fil
#########################################################
import pandas as pd
df = pd.DataFrame({'k_vals': k_vals, 'm_vals': m_vals})
df.to_csv('kalibrering' + name + '.csv', index=False)

