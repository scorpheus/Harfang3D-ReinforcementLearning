import gs
import math


def create_surface(id, array):
	"""Create an surface geometry"""
	geo = gs.CoreGeometry()
	material_path = "@core/materials/default.mat"

	geo.SetName("@gen/iso_{0}".format(id))

	geo.AllocateMaterialTable(1)
	geo.SetMaterial(0, material_path, True)

	# generate vertices
	if not geo.AllocateVertex(array.size):
		return None

	# send the vertices to the geometry with scaling them down to the right size
	count = 0
	scale = 0.02
	for x in range(array.shape[0]):
		for y in range(array.shape[1]):
			geo.SetVertex(count, x*scale, y*scale, array[x, y])
			count += 1

	# build polygons
	nb_poly = (array.shape[0]-1) * (array.shape[1]-1)
	if not geo.AllocatePolygon(nb_poly):
		return None

	for n in range(nb_poly):
		geo.SetPolygon(n, 4, 0)

	if not geo.AllocatePolygonBinding():
		return None

	count = 0
	for x in range(array.shape[0]-1):
		for y in range(array.shape[1]-1):
			geo.SetPolygonMaterialIndex(count, 0)
			geo.SetPolygonBinding(count,  [x + y * array.shape[0], x+1 + y * array.shape[0], x+1 + (y+1) * array.shape[0], x + (y+1) * array.shape[0]])
			count += 1

	geo.ComputeVertexNormal(math.radians(40))
	geo.ComputeVertexTangent()

	return gs.GetPlus().CreateGeometry(geo), geo

