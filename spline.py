"""
@author: Mohsin
"""
from scipy import interpolate
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import torch

class Spline():
    
    def __init__(self, times, x_coord, y_coord):

        n = len(times)
        assert n == len(x_coord), "lengths don't match"
        assert n == len(y_coord), "lengths don't match"
        assert n >= 2, "not long enough"

        self.times = times
        
        row_length = 4 * (n-1)

        self.A_x = []
        self.b_x = []

        self.A_y = []
        self.b_y = []

        for i in np.arange(0, n):
            t = times[i]
            x = x_coord[i]
            y = y_coord[i]

            f_x_prime = np.zeros(row_length)
            f_y_prime = np.zeros(row_length)

            #position row
            if i != 0:
                f_x = np.zeros(row_length)
                f_x[4*(i-1)] = t**3
                f_x[4*(i-1) + 1] = t**2
                f_x[4*(i-1) + 2] = t
                f_x[4*(i-1) + 3] = 1
                self.A_x.append(f_x)
                self.b_x.append(x)

                f_x_prime[4*(i-1)] = 3*t**2
                f_x_prime[4*(i-1) + 1] = 2*t
                f_x_prime[4*(i-1) + 2] = 1

                f_y = np.zeros(row_length)
                f_y[4*(i-1)] = t**3
                f_y[4*(i-1) + 1] = t**2
                f_y[4*(i-1) + 2] = t
                f_y[4*(i-1) + 3] = 1
                self.A_y.append(f_y)
                self.b_y.append(y)

                f_y_prime[4*(i-1)] = 3*t**2
                f_y_prime[4*(i-1) + 1] = 2*t
                f_y_prime[4*(i-1) + 2] = 1

            if i != n-1:
                f_x = np.zeros(row_length)
                f_x[4*i] = t**3
                f_x[4*i + 1] = t**2
                f_x[4*i + 2] = t
                f_x[4*i + 3] = 1
                self.A_x.append(f_x)
                self.b_x.append(x)


                f_x_prime[4*i] = -3*t**2
                f_x_prime[4*i + 1] = -2*t
                f_x_prime[4*i + 2] = -1

                f_y = np.zeros(row_length)
                f_y[4*i] = t**3
                f_y[4*i + 1] = t**2
                f_y[4*i + 2] = t
                f_y[4*i + 3] = 1
                self.A_y.append(f_y)
                self.b_y.append(y)


                f_y_prime[4*i] = -3*t**2
                f_y_prime[4*i + 1] = -2*t
                f_y_prime[4*i + 2] = -1

            self.A_x.append(f_x_prime)
            self.b_x.append(0)

            self.A_y.append(f_y_prime)
            self.b_y.append(0)

            if i != 0 and i != n-1:

                #second derivative row
                f_x_dprime = np.zeros(row_length)
                f_x_dprime[4*(i-1)] = 6*t
                f_x_dprime[4*(i-1) + 1] = 2

                f_x_dprime[4*i] = -6*t
                f_x_dprime[4*i + 1] = -2

                self.A_x.append(f_x_dprime)
                self.b_x.append(0)

                f_y_dprime = np.zeros(row_length)
                f_y_dprime[4*(i-1)] = 6*t
                f_y_dprime[4*(i-1) + 1] = 2

                f_y_dprime[4*i] = -6*t
                f_y_dprime[4*i + 1] = -2

                self.A_y.append(f_y_dprime)
                self.b_y.append(0)

        self.A_x = torch.from_numpy(np.array(self.A_x))
        self.A_y = torch.from_numpy(np.array(self.A_y))
        self.b_x = torch.tensor(self.b_x, dtype=torch.float64)
        self.b_y = torch.tensor(self.b_y, dtype=torch.float64)


    def evaluate(self, t, der=0):
        coeffs_x = torch.matmul(torch.inverse(self.A_x), self.b_x)
        coeffs_y = torch.matmul(torch.inverse(self.A_y), self.b_y)

        i = 0

        while self.times[i+1] < t:
            i += 1

        a_x = coeffs_x[4*i]
        b_x = coeffs_x[4*i + 1]
        c_x = coeffs_x[4*i + 2]
        d_x = coeffs_x[4*i + 3]

        a_y = coeffs_y[4*i]
        b_y = coeffs_y[4*i + 1]
        c_y = coeffs_y[4*i + 2]
        d_y = coeffs_y[4*i + 3]

        if der==0:
            res_x = a_x*t**3 + b_x*t**2 + c_x*t + d_x
            res_y = a_y*t**3 + b_y*t**2 + c_y*t + d_y
        elif der==1:
            res_x = 3*a_x*t**2 + 2*b_x*t + c_x
            res_y = 3*a_y*t**2 + 2*b_y*t + c_y

        return res_x, res_y



if __name__=="__main__":
    cs = Spline(np.arange(9), [0, 1, 2, 1, 0, -1, -2, -1, 0], [0, 1, 0, -1, 0, 1, 0, -1, 0])

    times = np.linspace(0, 8, 80)

    xs = []
    ys = []

    for time in times:
        x, y = cs.evaluate(time)
        xs.append(x)
        ys.append(y)

    plt.plot(xs, ys)
    plt.show()



