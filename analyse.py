from PIL import Image, ImageFilter, ImageOps
import glob
import random

wisdom_path = "wisdom/*.jpeg"

filenames = glob.glob(wisdom_path)

filename = random.choice(filenames)

#filename = "wisdom/wisdom-0086.jpeg"

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
rhos = np.linspace(-diag_len, diag_len, diag_len * 2.0)  # range from - to + diag_len

# Cache some resuable values
cos_t = np.cos(thetas)
sin_t = np.sin(thetas)
num_thetas = len(thetas)

# Hough accumulator array of theta vs rho
half_page_height = num_thetas
page_height = 2 * half_page_height
accumulator_height = page_height * 4
accumulator_width = 2 * diag_len
accumulator_index = 0
output_index = 0
accumulator = np.zeros((accumulator_height, accumulator_width), dtype=np.uint8)
y_idxs, x_idxs = np.nonzero(np.asarray(im))  # (row, col) indexes to ink pixels


brightness = 5

scanner = np.zeros((width, height), dtype=np.uint8)

started_image = False

def add(column, row):
  accumulator[column, row] = min(accumulator[column, row] + brightness, 255)

# Vote in the hough accumulator
with imageio.get_writer('output.gif', mode='I', fps=50) as writer:
  #for each column (as if it was being scanned in)


  for column in reversed(range(width)):
    print(f"accumulator_index {accumulator_index}")

    image_data = np.asarray(im)

    column_pixels = image_data[:,column]

    x_idxs = np.nonzero(column_pixels)[0]  # (row, col) indexes to ink pixels
    started_image |= (len(x_idxs) > 0)


    for i in range(len(x_idxs)):  # for each ink pixel in the column
      x = x_idxs[i]
      y = column

      for t_idx in range(num_thetas):  # for each angle

        t_offset_idx = (t_idx + accumulator_index) % num_thetas

        # Calculate rho. diag_len is added for a positive index
        #rho = int(x * cos_t[t_offset_idx]  + y * sin_t[t_offset_idx] + diag_len)
        rho = int((x - (height / 2)) * cos_t[t_offset_idx]  + (y-(width/2)) * sin_t[t_offset_idx] + diag_len)

        if (t_idx + accumulator_index) % page_height +1 > half_page_height:
          add(t_idx + accumulator_index + page_height, (2 * diag_len) - 1 - rho)
          add(t_idx + accumulator_index + page_height + half_page_height, rho)
          add(t_idx + accumulator_index + page_height*2 , (2 * diag_len) - 1 - rho)
          #add(t_idx + accumulator_index + page_height*2 + half_page_height, rho)

        else:
          add(t_idx + accumulator_index + page_height, rho)
          add(t_idx + accumulator_index + page_height + half_page_height, (2 * diag_len) - 1 - rho)
          add(t_idx + accumulator_index + page_height*2, rho)
          #add(t_idx + accumulator_index + page_height*2 + half_page_height, (2 * diag_len) - 1 - rho)

    accumulator_index += 1


    if started_image:
      writer.append_data(np.copy(accumulator[output_index:output_index+page_height, :]))
      output_index +=1

  for index in range(output_index, page_height*3):
    print(f"index {index}")
    writer.append_data(np.copy(accumulator[index:index + page_height, :]))



#output = Image.fromarray(accumulator)
#im.show()
#output.show()
#output.close()



