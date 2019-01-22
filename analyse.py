from PIL import Image, ImageFilter, ImageOps
import glob
import random

wisdom_path = "wisdom/*.jpeg"

filenames = glob.glob(wisdom_path)

filename = random.choice(filenames)

print(filename)
im = Image.open(filename)
print(im.size)

scale = 20

im = im.resize((int(im.size[0]/scale), int(im.size[1]/scale)), resample=Image.BICUBIC)

im = im.convert(mode="L", dither=250)
im = ImageOps.autocontrast(im)
im = ImageOps.invert(im)

#im.show()
#im.close()



import numpy as np
import imageio


# Rho and Theta ranges
thetas = np.deg2rad(np.arange(-90.0, 90.0))
width, height = im.size
diag_len = int(np.ceil(np.sqrt(width * width + height * height)))   # max_dist
rhos = np.linspace(-diag_len, diag_len, diag_len * 2.0)

# Cache some resuable values
cos_t = np.cos(thetas)
sin_t = np.sin(thetas)
num_thetas = len(thetas)

# Hough accumulator array of theta vs rho
accumulator = np.zeros((2*num_thetas, 2 * diag_len), dtype=np.uint8)
y_idxs, x_idxs = np.nonzero(np.asarray(im))  # (row, col) indexes to edges


frames = 50
frame_nth = int(len(x_idxs)/frames)
print(frame_nth)

brightness = 3

# Vote in the hough accumulator
with imageio.get_writer('output.gif', mode='I') as writer:
  for i in range(len(x_idxs)):
    x = x_idxs[i]
    y = y_idxs[i]

    for t_idx in range(num_thetas):
      # Calculate rho. diag_len is added for a positive index
      rho = int(x * cos_t[t_idx] + y * sin_t[t_idx] + diag_len)
      accumulator[t_idx, rho] += brightness
      accumulator[num_thetas+t_idx, (2 * diag_len)-1-rho] += brightness

    if (i%frame_nth)==0:
      writer.append_data(accumulator)


#output = Image.fromarray(accumulator)
#im.show()
#output.show()
#output.close()



