#library för hårdvara
from pytictoc import TicToc
import numpy
from numpy import mod
t = TicToc()

#library för tidtagning och sparande av data.
import qwiic_tca9548a
import PyNAU7802
import smbus2
import pandas as pd

################################################################################
#här finns portarna som man vill koppla till på muxen
################################################################################
ports = [6, 2, 1, 0, 7, 5]
#skapar mux med address 0x70
mux = qwiic_tca9548a.QwiicTCA9548A(address=0x70)

#öppnar/stänger portar på muxen
def enable_port(mux: qwiic_tca9548a.QwiicTCA9548A, port):
    mux.enable_channels(ports[port])

def disable_port(mux: qwiic_tca9548a.QwiicTCA9548A, port):
    mux.disable_channels(ports[port])

#skapar bus för i2c kommunikation
bus = smbus2.SMBus(1)

###########################################################
#öppnar en port(port), läser av adc på den porten, stänger porten och returnerar result.
#################################################################
def get_scale(mux, port):
    
    enable_port(mux, port)
    result=adcs[port].getReading()
    disable_port(mux, port)
    return result


samplestr= input("Ange antalet samples:")
samples = int(samplestr)

##########################################################################
#Öppnar en port på muxen, skapar ett adc objekt för den porten och lägger till i listan adcs. stänger sedan porten.
##########################################################################

adcs = list()
for i in range(6):
    enable_port(mux, i)
    adc = PyNAU7802.NAU7802()
    adc.begin(bus)
    adcs += [adc]
    disable_port(mux, i)


##########################################################################
#skapar ett dictionary för varje ben
##########################################################################
dct = {}
for i in range(6):
    dct['leg_%s' % i] = []  

#########################################################################
#get scale på alla adc i ordningen de ligger i ports[]
#########################################################################
t.tic()
for i in range(samples * 6):
    dct['leg_%s' % mod(i,6)].append(get_scale(mux, mod(i,6)))
samples_div_tid = samples/t.tocvalue()
time = numpy.true_divide((numpy.arange(samples)), samples_div_tid)
Samples = numpy.arange(1,(samples+1))

#############################################################
#Sparar till fil
#############################################################
from datetime import datetime
now = datetime.now()
tid = now.strftime("%d/%m/%Y %H:%M:%S")
print(tid)
name = str(input('filnamn'))

df = pd.DataFrame({'Samples': Samples, 'leg0': dct['leg_0'], 'leg1': dct['leg_1'], 'leg2': dct['leg_2'], 'leg3': dct['leg_3'],'leg4': dct['leg_4'],'leg5': dct['leg_5'], 'time': time})
df.to_csv(name + '.csv', index=False)
