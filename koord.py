################################################################################
#Library för att importera datan och göra matematiska operationer
################################################################################
from tkinter import Y
import numpy as np
import pandas as pd
from pandas import *

################################################################################
#Specifiera namn på kalibreringsfilen för att importera korrektra k och m värden
################################################################################
clbrtn = str(input('Specify the name of the calibration file: '))
data1 = read_csv(clbrtn + '.csv')

################################################################################
#Skapar lista med m- och k-värden
################################################################################
m_vals = data1['m_vals'].tolist() 
k_vals = data1['k_vals'].tolist()

###############################################################################
#Specifierar och importerar dataframe med rådata från lastcellerna 
# och skapar en lista med nummer på samplarna
################################################################################
rawmeasure = str(input('Specify the name of the measurement file: '))
x = read_csv(rawmeasure + '.csv')
Samples = x['Samples'].tolist()


###############################################################################
#Koordinater för positioner där staticpodens ben är kopplad till translatorn(p1) 
#och statorn(po) samt för objektet som ska studeras(pous). 
################################################################################
p1 = np.array([
    [ 86.873,  67.477,  292.283],
    [ 101.873, 41.496 , 292.283],
    [ 15,     -108.972, 292.283],
    [-15,     -108.972, 292.283],
    [-101.873, 41.496,  292.283],
    [-86.873,  67.477,  292.283]]).transpose()

p0 = np.array([
    [ 15,       181.883,  0],
    [ 165.015, -77.951,   0],
    [ 150.015, -103.932,  0],
    [-150.015, -103.932,  0],
    [-165.015, -77.951,   0],
    [-15,       181.833,  0]]).transpose()

pous = np.array([
    [ 0,  0,  319.755],
    [ 0, 0 , 319.755],
    [ 0,     0, 319.755],
    [0, 0, 319.755],
    [0, 0,  319.755],
    [0,  0,  319.755]]).transpose()

###############################################################################
#Skapar tom listor för att kunna spara längden på benen(len_leg), 
# riktningsvektorerna(n_list), normaliserade riktningsvektorerna(n_list_norm), 
# rotationsaxlarnas längder(r_list) samt kryssprodukten av rotationsaxlarnas längder 
# och  normaliserade  riktningsvektorerna(tei)
################################################################################
len_leg = list()
n_list_norm= list()
r_list =list()
tei = list()

###############################################################################
#Beräknar längden av varje ben och sparar det i listan len_leg
################################################################################
for i in range(6):  
    len_leg.append(np.sqrt(np.power((p0[0,i]-p1[0,i]),2) + np.power((p0[1,i]-p1[1,i]),2) + np.power((p0[2,i]-p1[2,i]),2)))


for i in range(6):
        n =  p1[:,i] - p0[:, i]
        n_norm = n/len_leg[i]
        n_list_norm.append(n_norm)

for i in range(6):
    r = p1[:,i] - pous[:,i]
    r_list.append(r)

Atop = np.concatenate([ [(n_list_norm[i])] for i in range(6)], 0).T

for i in range(6):
    tei.append(np.cross(r_list[i],n_list_norm[i])*1e-3)


Abottom = np.concatenate([ [tei[i]] for i in range(6)], 0).T

A = np.concatenate([Atop, Abottom])

y = np.zeros((len(Samples),6),dtype=float)
print(A)
for i in range(len(Samples)):      
    for a in range(6):
        y[i,a] = ((x.iat[i,a+1]) - m_vals[a]) * k_vals[a] 
print(y)

#Slutligen V = A*y
V =[]
for i in range(len(Samples)):
    Vi = np.matmul(A,y[i,:])
    V.append(Vi)
exempelV = ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']
print(exempelV)
np.savetxt("foo.csv", V, delimiter=",")

