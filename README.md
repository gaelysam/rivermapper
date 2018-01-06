# River Mapper

Python script to transform a Digital Elevation Model (DEM) image into a map of rivers.
You need Python 3 with `numpy` and `imageio`.

Script execution:
`rivermapper.py input_image.tif output_image.tif [-l sea_level] [-s random_seed] [-c contrast] [-d output_bit_depth]`
or:
`rivermapper.py -i input_image.tif -o output_image.tif [-l sea_level] [-s random_seed] [-c contrast] [-d output_bit_depth]`

Used RAM: around 10 Mo per milion pixels (400 Mo for a 6001x6001 [SRTM image](http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp))
Time taken: it can take several minutes. The same SRTM image takes arount 20 minutes. Please be patient.

It should support most of image types (PNG, TIFF, JPG, BMP, ...) and bit depths (8, 16, 32, 64).

Behaviour:
* It creates river systems from start points (pixels near the sea, or on the edge of the map), by analysing the slope to find in which direction the water will flow, on every pixel. Rivers are the points that receive the water from numerous pixels (usually some thousands, or even millions).
* It supports basins. There are generally not naturals, but still exist in most of the DEM, because of approximative data. It find the simplest way to get the river escape the basin.
* It can't determine rivers positions on too flat areas, because we need some slope to know where the water flows. In this case, rivers are set randomly.
* We obviously can't know how much water comes from outside of the map. So, the rivers that are on the edge of the map may have a smaller value than in the reality. There is not this problem for an island.

An example with the [Corsica](https://en.wikipedia.org/wiki/Corsica) island:

The original image in zip file: [corsica.zip](https://github.com/Gael-de-Sailly/rivermapper/files/189394/corse.zip)

Enhanced DEM to show the mountains and the valleys: ![corsica_enhanced](https://cloud.githubusercontent.com/assets/6905002/14042963/5371a7d0-f27f-11e5-946b-9ddafe1e0e91.png)
Rivers map built with RiverMapper: ![corsica_rivers](https://cloud.githubusercontent.com/assets/6905002/14042964/5ba01284-f27f-11e5-9fb9-77d98d53972c.png)
