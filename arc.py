#IDK what this means
from __future__ import annotations

import decimal
import math
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

class Arc:
    n_values = 0
    def __init__(self, name: str):
        #TODO more robust method than just having a 50 sized array
        self.arcVectorX = np.zeros((50), dtype = float)
        self.arcVectorY = np.zeros((50), dtype = float)
        #There is a better way to do this but I wanna test stuff quick
        n_values = 0

    def add(self, xval, yval): 
        if self.n_values < len(self.arcVectorX):
            self.arcVectorX[self.n_values] = xval
            #Invert y values so our charts don't look dumb
            self.arcVectorY[self.n_values] = yval * -1
        else:
            np.append(self.arcVectorX, xval)
            np.append(self.arcVectorY, yval)
        self.n_values+=1

    def print(self):
        print("Number of frames in arc:", self.n_values)
        for (i,j) in zip(self.arcVectorX, self.arcVectorY):
            print("X value is", i)
            print("Y value is", j)

    def plot(self):
        fig=plt.figure()
        ax=fig.add_axes([0,0,1,1])
        #slices in python are [inclusive,exclusive] for some reason
        x = self.arcVectorX[0:self.n_values]
        y = self.arcVectorY[0:self.n_values]
        ax.scatter(x, y, color='g')
        coefs = np.polynomial.polynomial.polyfit(x,y,10)
        ffit = np.polynomial.polynomial.Polynomial(coefs)
        plt.plot(x, ffit(x))
        plt.show()

