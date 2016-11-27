import random
from create_surface import *
from rlnet import *
import test_car as experiment

gs.LoadPlugins()

plus = gs.GetPlus()
plus.CreateWorkers()

plus.RenderInit(1024, 768)

plus.GetRendererAsync().SetVSync(False)

scn = plus.NewScene()
scn.GetPhysicSystem().SetDebugVisuals(True)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 10, -6)))
plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(-8, 10, -6)))

# Initialize experience replay object
exp_replay = ExperienceReplay(max_memory=max_memory)

# Initialize model
model = RLNet(experiment.get_name(), experiment.num_inputs, experiment.num_actions)

# create the environment to evaluate score
experiment.initialize_environment(scn)

fps = gs.FPSController(0, 2, -10)

# parameters
score = 0.0
fixed_timestep = 1.0/60
nb_frame = 0
initialize = True


while not plus.IsAppEnded(plus.EndOnDefaultWindowClosed): #plus.EndOnEscapePressed |
	dt_sec = plus.UpdateClock()

	# fixed_timestep = dt_sec.to_sec()
	# move camera
	fps.UpdateAndApplyToNode(cam, dt_sec)

	# test
	if plus.KeyDown(gs.InputDevice.KeyR):
		experiment.initiate_test_subject(scn)

	experiment.update(fixed_timestep, model)

	# if need reset, game over
	if initialize or experiment.is_game_over():
		initialize = False
		loss = 0.
		experiment.initiate_test_subject(scn)
		game_over = False
		# get initial input
		input_t = experiment.get_inputs()
		print("Epoch {:d} | Loss {:.4f} | Win count {}".format(nb_frame, loss))

	else:
		input_tm1 = input_t
		# get next action
		if np.random.rand() <= epsilon:
			action = np.random.randint(0, num_actions, size=1)
		else:
			q = model.predict(input_tm1)
			action = np.argmax(q[0])

		# apply action, get rewards and new state
		input_t, reward, game_over = experiment.act(action)

		# store experience
		exp_replay.remember([input_tm1, action, reward, input_t], game_over)

		# adapt model
		inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)

		loss += model.train_on_batch(inputs, targets)

	nb_frame += 1
	plus.UpdateScene(scn, gs.time(fixed_timestep))
	plus.Text2D(5, 20, "Epoch {:d} | Loss {:.4f}".format(nb_frame, loss))
	plus.Text2D(5, 5, "Move around with QSZD, left mouse button to look around")
	plus.Flip()
