import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def gaussian(x, a, mu, fwhm, offset_y):
    sigma = fwhm / 2.3548
    return a * np.exp(-(x - mu)**2 / (2 * sigma**2)) + offset_y

xdata = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 \
,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47 \
,48,49,50,51,52,53,54,55,56,57,58,59,60,61])
    
# Values extracted from random data file.fits to test gaussian fit curves
ydata = np.array([ 0.,0.,0.,0.,0.1391094,0.04629678, \
 -0.02553891,  0.10027689,  0.10803553,  0.08800025 , 0.0534449,0.13564657, \
  0.05307769,  0.03159827,  0.04164632,  0.0547316,0.12864335,  0.04677442, \
  0.01388375,  0.15470354, -0.00863961,  0.36480582,  0.33426622,  0.43566123, \
  0.53951436,  0.7806605,0.82980007,  1.0643952,1.3019139,1.6338588, \
  1.605978, 1.7610677,1.7031754,1.5839152,1.4669276,1.2196615, \
  1.1313053,0.7762969,0.5651505,0.5587464,0.43632224,  0.2991539, \
  0.13368745,  0.26487035,  0.14065695,  0.2946713,0.22862244,  0.21456613, \
  0.23047335,  0.1276456,0.21033469,  0.23335433,  0.17760806,  0.14199205, \
  0.17639747,  0.20344494,  0.2336405,0.16060516,  0.,0., \
  0.,0.])

plt.plot(xdata, ydata, 'b-', label='data')

fit_bounds = ([0, 26., 5., 0], [1.75, 34., 15., 0.2])
popt, pcov = curve_fit(gaussian, xdata, ydata, bounds=fit_bounds)
plt.plot(xdata, gaussian(xdata, *popt), 'r-', label='fit')

ydata_fited = gaussian(xdata, popt[0], popt[1], popt[2], popt[3])

plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()
print('params', popt)
print('y fited', ydata_fited)
