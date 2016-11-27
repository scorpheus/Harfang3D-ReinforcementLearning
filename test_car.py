import gs
from create_surface import *

plus = gs.GetPlus()

ground = None
car = None
car_physic = None
num_inputs = 5
num_actions = 3
inputs = []
scene = None
scene_simple_graphic = None
prev_pos = gs.Vector3(0, 0, 0)


def get_name():
	return "car"


def initialize_environment(scn):
	global car, car_physic, ground, scene, scene_simple_graphic
	scene = scn
	scn.GetPhysicSystem().SetTimestep(1.0/120)

	scene_simple_graphic = gs.SimpleGraphicSceneOverlay(False)
	scene.AddComponent(scene_simple_graphic)

	ground = plus.AddPhysicPlane(scn)[0]

	car, car_physic = plus.AddPhysicCube(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 0.5, 0)), 0.5, 1, 1, 10)

	# add walls
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(0, 0, -1.1), gs.Vector3(0, 0, 0)), 4, 3, 1, 0)

	plus.AddPhysicCube(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(-2, 0, 2)), 1, 3, 5, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(2, 0, 2)), 1, 3, 5, 0)

	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(-1, 0, 6), gs.Vector3(0, 0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(3, 0, 6), gs.Vector3(0, 0.7, 0)), 1, 3, 4, 0)

	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(1, 0, 8), gs.Vector3(0, 0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(5, 0, 8), gs.Vector3(0, 0.7, 0)), 1, 3, 4, 0)

	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(1, 0, 10), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(5, 0, 10), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)

	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(-1, 0, 12), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(3, 0, 12), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(-2, 0, 14), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)
	plus.AddPhysicCube(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(1, 0, 14), gs.Vector3(0, -0.7, 0)), 1, 3, 4, 0)


def initiate_test_subject(scn):
	car_physic.SetIsSleeping(False)
	car_physic.ResetWorld(gs.Matrix4.TranslationMatrix(gs.Vector3(0, 0.5, 0)))


def draw_cross(pos):
	size = 0.5
	scene_simple_graphic.Line(pos.x-size, pos.y, pos.z,
	                          pos.x+size, pos.y, pos.z,
	                          gs.Color.Red, gs.Color.Red)
	scene_simple_graphic.Line(pos.x, pos.y-size, pos.z,
	                          pos.x, pos.y+size, pos.z,
	                          gs.Color.Red, gs.Color.Red)
	scene_simple_graphic.Line(pos.x, pos.y, pos.z-size,
	                          pos.x, pos.y, pos.z+size,
	                          gs.Color.Red, gs.Color.Red)


def get_inputs():
	global inputs

	length_ray = 10
	inputs = []
	# get input
	pos = car.GetTransform().GetPosition()
	pos.y += 0.5
	front_vec = car.GetTransform().GetWorld().GetZ() * 0.51
	pos += front_vec

	angles = [-1.57/3*2, -1.57/3, 0, 1.57/3*2, 1.57/3]

	for id, angle in enumerate(angles):
		rotate_front = (gs.Matrix3.RotationMatrixYAxis(angle) * front_vec).Normalized()
		has_hit, hit = scene.GetSystem("Physic").Raycast(pos, rotate_front, 255, length_ray)
		if has_hit:
			length = gs.Vector3.Dist(pos, hit.GetPosition())
			inputs.append(length / length_ray)
			scene_simple_graphic.Line(pos.x, pos.y, pos.z, pos.x + rotate_front.x * length, pos.y + rotate_front.y * length, pos.z + rotate_front.z * length, gs.Color.White, gs.Color.White)
			draw_cross(hit.GetPosition())
			draw_cross(pos)
		else:
			inputs.append(1)
			scene_simple_graphic.Line(pos.x, pos.y, pos.z, pos.x + rotate_front.x * length_ray, pos.y + rotate_front.y * length_ray, pos.z + rotate_front.z * length_ray, gs.Color.White, gs.Color.White)

	return inputs


def get_score(scn):
	global prev_pos
	score = 0
	# BAD look if the car collide, and if it's not with the ground
	if scn.GetPhysicSystem().HasCollided(car):
		for pair in scn.GetPhysicSystem().GetCollisionPairs(car):
			if ground != pair.GetNodeA() and ground != pair.GetNodeB():
				score -= 1

	# BAD if the input is low, too near the wall
	for input in inputs:
		if input < 0.3:
			score -= 1

	# BAD if didn't move
	if gs.Vector3.Dist2(prev_pos, car.GetTransform().GetPosition()) < 0.01:
		score -= 1

	# GOOD if progress
	score += gs.Vector3.Dist(car.GetTransform().GetPosition(), gs.Vector3(0, 0.5, 0)) * 200.0
	return score


def is_game_over():
	return False


def update(scn, dt_sec, action):
	# rotate
	rotate_impulse = action[0] * 2 - 1.0
	power_impulse = (action[1] * 2 - 1) * 1.5
	# print(rotate_impulse)

	pos = car.GetTransform().GetPosition()
	pos.y += 0.5
	front_vec = car.GetTransform().GetWorld().GetZ() * 0.51
	pos += front_vec

	vec_impulse = gs.Matrix3.RotationMatrixYAxis(rotate_impulse) * front_vec * power_impulse
	scene_simple_graphic.Line(pos.x, pos.y, pos.z, pos.x + vec_impulse.x, pos.y + vec_impulse.y, pos.z + vec_impulse.z, gs.Color.Green, gs.Color.Green)

	car_physic.ApplyLinearImpulse(gs.Matrix3.RotationMatrixYAxis(rotate_impulse) * front_vec * power_impulse * dt_sec.to_sec())

	return get_inputs(), get_score(scn), is_game_over()
