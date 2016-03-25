from wand.image import Image
from heapq import heappush, heappop, heapify
from random import *
from tkinter import simpledialog, filedialog, messagebox, Tk
import sys
from math import sqrt, ceil
from array import array

master = Tk()

print("Asking input file")
fname = filedialog.askopenfilename(parent=master, title="Input image")

sys.setrecursionlimit(65536)

print("Reading image")
with Image(filename=fname) as img:
	blob = img.make_blob("gray")
	W = img.width
	H = img.height
	size = W * H
	signed = messagebox.askyesno("Signed image", "Is the image signed?")
	depth = img.depth

if messagebox.askyesno("Seed", "Use custom random seed?"):
	cseed = simpledialog.askstring("Seed", "Enter the seed. All characters are accepted.\nThe use of the random is to place rivers randomly where the data do not allow to trace the river (too flat)")
	seed(a=cseed)

if depth == 8:
	typecode = "B"
elif depth == 16:
	typecode = "H"
elif depth == 32:
	typecode = "L"
elif depth == 64:
	typecode = "Q"

if signed:
	typecode = typecode.lower()

pixels = array(typecode, blob)

blob = None

print("Finding start points")

visited = [False for i in range(size)]

start_points = []

def add_start_point(i):
	start_points.append((pixels[i] + random(), i))
	visited[i] = True

initial_sea_level = 0
if signed:
	initial_sea_level = -(2 ** (depth-1))

SEA = simpledialog.askinteger("Sea level", "Sea level:", initialvalue=initial_sea_level, parent=master, minvalue=initial_sea_level)
SEA = SEA or float("-inf")

to_explore = 0

for x in range(1, W-1):
	for y in range(1, H-1):
		i = y * W + x
		if pixels[i] <= SEA:
			continue
		to_explore += 1
		if (pixels[i-1] <= SEA or pixels[i+1] <= SEA or pixels[i-W] <= SEA or pixels[i+W] <= SEA):
			add_start_point(i)

length_x = size - W
length_y = W - 1

for x in range(1, W-1):
	i = x
	if pixels[i] > SEA:
		add_start_point(i)
		to_explore += 1
	i += length_x
	if pixels[i] > SEA:
		add_start_point(i)
		to_explore += 1

for y in range(1, H-1):
	i = y * W
	if pixels[i] > SEA:
		add_start_point(i)
		to_explore += 1
	i += length_y
	if pixels[i] > SEA:
		add_start_point(i)
		to_explore += 1

print("Found", str(len(start_points)), "start points")

heap = start_points[:]
heapify(heap)

print("Building river trees:", str(to_explore), "points to visit")

links = array("l", range(size))

def try_push(i1, i2):
	if not visited[i2]:
		px = pixels[i2]
		if px > SEA:
			heappush(heap, (px + random(), i2))
			links[i2] = i1
			visited[i2] = True

def process_neighbors(i):
	x, y = i % W, i // W
	if x > 0:
		try_push(i, i-1)
	if x < W-1:
		try_push(i, i+1)
	if y > 0:
		try_push(i, i-W)
	if y < H-1:
		try_push(i, i+W)

while len(heap) > 0:
	t = heappop(heap)
	to_explore -= 1
	if to_explore % 1000000 == 0:
		print(str(to_explore // 1000000), "million points left", "Altitude:", int(t[0]), "Queue:", len(heap))
	process_neighbors(t[1])

visited = None
pixels = None

print("Calculating water quantity")

neighbors = [-W, -1, 1, W]
waterlist = array("L", [1 for i in range(size)])

def set_water(i):
	water = 1
	for neighbor in neighbors:
		i2 = i + neighbor
		if i2 < 0 or i2 >= size:
			continue
		if links[i2] == i:
			water += set_water(i2)
	waterlist[i] = water
	return water

maxwater = 0
for start in start_points:
	water = set_water(start[1])
	if water > maxwater:
		maxwater = water

print("Maximal water quantity:", str(maxwater))

links = None

print("Generating image data")

contrast = simpledialog.askfloat("Contrast", "Contrast of the image:\nThe higher it is, the more visible are the small rivers.", initialvalue=3.0, parent=master, minvalue=0)

power = 1 / contrast
coeff = 65535 / (maxwater ** power - 1)
	
rawdata = array("H")
for i in range(size):
	value = min(ceil((waterlist[i] ** power - 1) * coeff), 65535)
	rawdata.append(value)

waterlist = None

print("Converting to bytes")

rawdata = rawdata.tobytes()

print("Generating image")

img = Image(blob=rawdata, width=W, height=H, format="gray", depth=16)
print("Converting image")
img.convert("tiff")
print("Asking output file")
target = filedialog.asksaveasfilename(parent=master, defaultextension=".tif", title="Output image")
print("Writing image")
img.save(filename=target)
