import numpy as np

c = np.linspace(1, 10, 10)

level_min = 20  # %
level_max = 80

initial_min = np.nanmin(c)
initial_max = np.nanmax(c)

c -= initial_min
c /= initial_max - initial_min

c = np.sqrt(c)
min_value = np.nanpercentile(c, level_min)
max_value = np.nanpercentile(c, level_max)
c[c < min_value] = min_value
c[c > max_value] = max_value

c = np.power(c, 2)
c *= initial_max - initial_min
c += initial_min

