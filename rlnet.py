import os
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd

# parameters
epsilon = .1  # exploration
num_actions = 3  # [move_left, stay, move_right]
epoch = 1000
max_memory = 500
hidden_size = 100
batch_size = 50
grid_size = 10


def create_model(name, nb_input, num_actions):
	model = Sequential()
	model.add(Dense(hidden_size, input_shape=(nb_input,), activation='relu'))
	model.add(Dense(hidden_size, activation='relu'))
	model.add(Dense(num_actions))
	model.compile(sgd(lr=.2), "mse")

	# to load weight pre learned
	if os.path.exists("weight_{0}.h5".format(name)):
		model.load_weights("weight_{0}.h5".format(name))
	return model


class ExperienceReplay(object):
	def __init__(self, max_memory=100, discount=.9):
		self.max_memory = max_memory
		self.memory = list()
		self.discount = discount

	def remember(self, states, game_over):
		# memory[i] = [[state_t, action_t, reward_t, state_t+1], game_over?]
		self.memory.append([states, game_over])
		if len(self.memory) > self.max_memory:
			del self.memory[0]

	def get_batch(self, model, batch_size=10):
		len_memory = len(self.memory)
		num_actions = model.output_shape[-1]
		env_dim = self.memory[0][0][0].shape[1]
		inputs = np.zeros((min(len_memory, batch_size), env_dim))
		targets = np.zeros((inputs.shape[0], num_actions))
		for i, idx in enumerate(np.random.randint(0, len_memory, size=inputs.shape[0])):
			state_t, action_t, reward_t, state_tp1 = self.memory[idx][0]
			game_over = self.memory[idx][1]

			inputs[i:i+1] = state_t
			# There should be no target values for actions not taken.
			# Thou shalt not correct actions not taken #deep
			targets[i] = model.predict(state_t)[0]
			Q_sa = np.max(model.predict(state_tp1)[0])
			if game_over:  # if game_over is True
				targets[i, action_t] = reward_t
			else:
				# reward_t + gamma * max_a' Q(s', a')
				targets[i, action_t] = reward_t + self.discount * Q_sa
		return inputs, targets


class RLNet(object):
	def __init__(self, name, nb_input, num_actions):
		self.model = create_model(name, nb_input, num_actions)

	# Save trained model weights and architecture, this will be used by the visualization code
	model.save_weights("model.h5", overwrite=True)
	with open("model.json", "w") as outfile:
		json.dump(model.to_json(), outfile)
