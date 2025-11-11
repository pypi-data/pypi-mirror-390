import cv2
import numpy as np
from matplotlib import pyplot as plt
# Loading source image
src_image = cv2.imread("images/map_x_y.png")
# Defining the kernel of size 3x3
kernel = np.array([
  [1, 1, 1],
  [1, 1, 1],
  [1, 1, 1]
])

print(src_image)
 
resulting_image = cv2.filter2D(src_image, -1, kernel)

#print(resulting_image)
 
# cv2.imshow("original image", src_image)
# cv2.imshow("filter2d image", resulting_image)
# cv2.imwrite("Filter2d Sharpened Image.jpg", resulting_image)
# cv2.waitKey()
# cv2.destroyAllWindows()


plt.imshow(resulting_image, interpolation='nearest')
plt.show()