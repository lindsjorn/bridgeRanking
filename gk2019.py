# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 11:11:10 2019

@author: u35249
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as scp

pd.read_csv(r'C:\Users\u35249\DataDiv\gk2019.csv',index_col=0)
df = pd.read_csv(r'C:\Users\u35249\DataDiv\gk2019.csv',index_col=0)

x = df.watt.values
y = df.tid.values

#z = np.polyfit(x, y, 2)
#f = np.poly1d(z)
#x_new = np.linspace(x[0], x[-1]+250, 50)
#y_new = f(x_new)
#
#plt.plot(x,y,'o', x_new, y_new)
#plt.xlim([x[0]-1, x[-1] + 250 ])
#plt.show()

def func(x,a,c,d):
    return a*np.exp(-c*x)+d
    
popt,pcov = scp.optimize.curve_fit(func,x,y,p0=(500,0.001,300))
x_new = np.linspace(x[0], x[-1]+250, 50)
y_new = func(x_new,*popt)

plt.plot(x,y,'o', x_new, y_new)
plt.xlim([x[0]-1, x[-1] + 250 ])
plt.show()