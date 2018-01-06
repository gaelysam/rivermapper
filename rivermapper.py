#!/usr/bin/env python3

from heapq import heappush, heappop, heapify
import sys
import numpy as np
import imageio

file_input = None
file_output = None

n_args = len(sys.argv)
i = 1
n = 1
sea_level = -128
seed = None
contrast = 3
bit_depth = 8
while i < n_args:
	arg = sys.argv[i]
	if len(arg) == 0:
		i += 1
		continue
	if arg[0] == "-":
		l = arg[1]
		if l == "l":
			sea_level = int(sys.argv[i+1])
			i += 2
			continue
		if l == "s":
			seed = int(sys.argv[i+1])
			i += 2
			continue
		if l == "c":
			contrast = float(sys.argv[i+1])
			i += 2
			continue
		if l == "d":
			bit_depth = int(sys.argv[i+1])
			i += 2
			continue
		if l == "i":
			file_input = sys.argv[i+1]
			i += 2
			continue
		if l == "o":
			file_output = sys.argv[i+1]
			i += 2
			continue
	else:
		if n == 2:
			file_output = arg
			n += 1
		if n == 1:
			file_input = arg
			n += 1
	i += 1

if not file_input:
	raise ValueError("No filename given for input")

if not file_output:
	raise ValueError("No filename given for output")

if seed:
	numpy.random.seed(seed=seed)

sys.setrecursionlimit(65536)

print("Reading image")
heightmap = np.array(imageio.imread(file_input))
shape = heightmap.shape
(X, Y) = shape

print("Finding start points")


visited = np.zeros(shape, dtype=bool)

start_points = []

def add_start_point(x, y):
	start_points.append((heightmap[x, y] + np.random.random(), x, y))
	visited[x, y] = True

to_explore = 0

for x in range(1, X-1):
	for y in range(1, Y-1):
		if heightmap[x, y] <= sea_level:
			continue
		to_explore += 1
		if to_explore % 1000000 == 0:
			print("Found", str(to_explore // 1000000), "millions points to explore")
		if (heightmap[x-1, y] <= sea_level or heightmap[x+1, y] <= sea_level or heightmap[x, y-1] <= sea_level or heightmap[x, y+1] <= sea_level):
			add_start_point(x, y)

for x in range(X):
	if heightmap[x, 0] > sea_level:
		add_start_point(x, 0)
		to_explore += 1
	if heightmap[x, -1] > sea_level:
		add_start_point(x, Y-1)
		to_explore += 1

for y in range(1, Y-1):
	if heightmap[0, y] > sea_level:
		add_start_point(0, y)
		to_explore += 1
	if heightmap[-1, y] > sea_level:
		add_start_point(X-1, y)
		to_explore += 1

print("Found", str(len(start_points)), "start points")

heap = start_points[:]
heapify(heap)

print("Building river trees:", str(to_explore), "points to visit")

flow_dirs = np.zeros(shape, dtype=np.int8)

# Directions:
#	1: +x
#	2: +y
#	4: -x
#	8: -y

def try_push(x, y): # try_push does 2 things at once: returning whether water can flow, and push the upward position in heap if yes.
	if not visited[x, y]:
		h = heightmap[x, y]
		if h > sea_level:
			heappush(heap, (h + np.random.random(), x, y))
			visited[x, y] = True
			return True
	return False

def process_neighbors(x, y):
	dirs = 0
	if x > 0 and try_push(x-1, y):
		dirs+= 1
	if y > 0 and try_push(x, y-1):
		dirs += 2
	if x < X-1 and try_push(x+1, y):
		dirs += 4
	if y < Y-1 and try_push(x, y+1):
		dirs += 8
	flow_dirs[x, y] = dirs

while len(heap) > 0:
	t = heappop(heap)
	to_explore -= 1
	if to_explore % 1000000 == 0:
		print(str(to_explore // 1000000), "million points left", "Altitude:", int(t[0]), "Queue:", len(heap))
	process_neighbors(t[1], t[2])

visited = None
heightmap = None

print("Calculating water quantity")

waterq = np.ones(shape)

def set_water(x, y):
	water = 1
	dirs = flow_dirs[x, y]

	if dirs % 2 == 1:
		water += set_water(x-1, y)
	dirs //= 2
	if dirs % 2 == 1:
		water += set_water(x, y-1)
	dirs //= 2
	if dirs % 2 == 1:
		water += set_water(x+1, y)
	dirs //= 2
	if dirs % 2 == 1:
		water += set_water(x, y+1)
	waterq[x, y] = water
	return water

maxwater = 0
for start in start_points:
	water = set_water(start[1], start[2])
	if water > maxwater:
		maxwater = water

print("Maximal water quantity:", str(maxwater))

flow_dirs = None

print("Generating image")
if bit_depth <= 8:
	bit_depth = 8
	dtype = np.uint8
elif bit_depth <= 16:
	bit_depth = 16
	dtype = np.uint16
elif bit_depth <= 32:
	bit_depth = 32
	dtype = np.uint32
else:
	bit_depth = 64
	dtype = np.uint64

maxvalue = 2 ** bit_depth - 1
power = 1 / contrast
coeff = maxvalue / (maxwater ** power)

data = np.floor((waterq ** power) * coeff).astype(dtype)

waterq = None

imageio.imwrite(file_output, data)
