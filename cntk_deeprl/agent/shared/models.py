# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================
"""A set of predefined models used by Q learning or Actor-Critic."""

import cntk as C
import numpy as np

import ast

def custom_network(shape_of_inputs,
		    number_of_outputs,
		    loss_function=None,
		    use_placeholder_for_input=False):
	"""Feedforward network to approximate Q or log of pi.

	Args:
	    shape_of_inputs: tuple of array (input) dimensions.
	    number_of_outputs: dimension of output, equals the number of
		possible actions.
	    model_hidden_layers: string representing a list of integers
		corresponding to number of nodes in each hidden layer.
	    loss_function: if not specified, use squared loss by default.
	    use_placeholder_for_input: if true, inputs have to be replaced
		later with actual input_variable.

	Returns: a Python dictionary with string valued keys including
	    'inputs', 'outputs', 'loss' and 'f'.
	"""
	# input/output
	inputs = C.ops.placeholder(shape=shape_of_inputs) \
	    if use_placeholder_for_input \
	    else C.ops.input_variable(shape=shape_of_inputs, dtype=np.float32)
	outputs = C.ops.input_variable(shape=(number_of_outputs,), dtype=np.float32)

	# network structure
	model_hidden_layers = '[100, 75, 75, 75, 75, 25]'
	hidden_layers = ast.literal_eval(model_hidden_layers)
	#f = C.layers.Sequential([
	#    C.layers.For(range(len(hidden_layers)),
	#	lambda h: C.layers.Dense(hidden_layers[h], activation=C.ops.relu)),
	#    C.layers.Dense(number_of_outputs, activation=None)
	#])(inputs)
	f = C.layers.Sequential([
	    C.layers.Convolution2D((1,5), num_filters=16, pad=True, reduction_rank=0, activation=C.ops.relu),
	    C.layers.Convolution2D((1,5), num_filters=24, pad=True, reduction_rank=1, activation=C.ops.relu),
	    C.layers.Convolution2D((1,5), num_filters=32, pad=False, reduction_rank=1, activation=C.ops.relu),
	    #C.layers.Convolution2D((2,5), num_filters=32, pad=False, reduction_rank=1, activation=C.ops.relu),
	    #C.layers.MaxPooling((1,3), pad=False),
	#    C.layers.For(range(len(hidden_layers)),
	#	lambda h: C.layers.Sequential([C.layers.Dense(hidden_layers[h], activation=C.ops.relu))]),
		#C.layers.Dense(180, activation=None),
		#C.layers.BatchNormalization(),
		#C.layers.Activation(activation=C.ops.relu),
		#C.layers.Dropout(0.2),
		#C.layers.Dense(140, activation=C.ops.relu),
		C.layers.Dense(120, activation=C.ops.relu),
		C.layers.Dense(100, activation=C.ops.relu),
		C.layers.Dense(50, activation=C.ops.relu),
	    C.layers.Dense(number_of_outputs, activation=None)
	])(inputs)

	if loss_function is None:
	    loss = C.losses.squared_error(f, outputs)
	else:
	    loss = loss_function(f, outputs)

	return {
	    'inputs': inputs,
	    'outputs': outputs,
	    'f': f,
	    'loss': loss
	}

class Models:
    """A set of predefined models to approximate Q or log of pi (policy).

    The loss function needs to be 'cross_entropy_with_softmax' for policy
    gradient methods.
    """

    @staticmethod
    def feedforward_network(shape_of_inputs,
                            number_of_outputs,
                            model_hidden_layers,
                            loss_function=None,
                            use_placeholder_for_input=False):
        """Feedforward network to approximate Q or log of pi.

        Args:
            shape_of_inputs: tuple of array (input) dimensions.
            number_of_outputs: dimension of output, equals the number of
                possible actions.
            model_hidden_layers: string representing a list of integers
                corresponding to number of nodes in each hidden layer.
            loss_function: if not specified, use squared loss by default.
            use_placeholder_for_input: if true, inputs have to be replaced
                later with actual input_variable.

        Returns: a Python dictionary with string valued keys including
            'inputs', 'outputs', 'loss' and 'f'.
        """
        # input/output
        inputs = C.ops.placeholder(shape=shape_of_inputs) \
            if use_placeholder_for_input \
            else C.ops.input_variable(shape=shape_of_inputs, dtype=np.float32)
        outputs = C.ops.input_variable(shape=(number_of_outputs,), dtype=np.float32)

        # network structure
        hidden_layers = ast.literal_eval(model_hidden_layers)
        f = C.layers.Sequential([
            C.layers.For(range(len(hidden_layers)),
                lambda h: C.layers.Dense(hidden_layers[h], activation=C.ops.relu)),
            C.layers.Dense(number_of_outputs, activation=None)
        ])(inputs)

        if loss_function is None:
            loss = C.losses.squared_error(f, outputs)
        else:
            loss = loss_function(f, outputs)

        return {
            'inputs': inputs,
            'outputs': outputs,
            'f': f,
            'loss': loss
        }

    @staticmethod
    def dueling_network(shape_of_inputs,
                        number_of_outputs,
                        model_hidden_layers,
                        loss_function=None,
                        use_placeholder_for_input=False):
        """Dueling network to approximate Q function.

        See paper at https://arxiv.org/pdf/1511.06581.pdf.

        Args:
            shape_of_inputs: tuple of array (input) dimensions.
            number_of_outputs: dimension of output, equals the number of
                possible actions.
            model_hidden_layers: in the form of "[comma-separated integers,
                [comma-separated integers], [comma-separated integers]]". Each
                integer is the number of nodes in a hidden layer.The
                first set of integers represent the shared component in dueling
                network. The second set correponds to the state value function
                V and the third set correponds to the advantage function A.
            loss_function: if not specified, use squared loss by default.
            use_placeholder_for_input: if true, inputs have to be replaced
                later with actual input_variable.

        Returns: a Python dictionary with string-valued keys including
            'inputs', 'outputs', 'loss' and 'f'.
        """
        # input/output
        inputs = C.ops.placeholder(shape=shape_of_inputs) \
            if use_placeholder_for_input \
            else C.ops.input_variable(shape=shape_of_inputs, dtype=np.float32)
        outputs = C.ops.input_variable(
            shape=(number_of_outputs,), dtype=np.float32)

        # network structure
        shared_hidden_layers, v_hidden_layers, a_hidden_layers =\
            Models._parse_dueling_network_structure(model_hidden_layers)
        # shared layers
        s = C.layers.For(
            range(len(shared_hidden_layers)),
            lambda h: C.layers.Dense(shared_hidden_layers[h], activation=C.ops.relu))(inputs)
        # Value function
        v = C.layers.Sequential([
            C.layers.For(
                range(len(v_hidden_layers)),
                lambda h: C.layers.Dense(v_hidden_layers[h], activation=C.ops.relu)),
            C.layers.Dense(1, activation=None)
        ])(s)
        # Advantage function
        a = C.layers.Sequential([
            C.layers.For(
                range(len(a_hidden_layers)),
                lambda h: C.layers.Dense(a_hidden_layers[h], activation=C.ops.relu)),
            C.layers.Dense(number_of_outputs, activation=None)
        ])(s)
        # Q = V + A - avg(A)
        avg_a = C.layers.AveragePooling((number_of_outputs,))(a)
        q = v + a - avg_a

        if loss_function is None:
            loss = C.losses.squared_error(q, outputs)
        else:
            loss = loss_function(q, outputs)

        return {
            'inputs': inputs,
            'outputs': outputs,
            'f': q,
            'loss': loss
        }

    @staticmethod
    def _parse_dueling_network_structure(hidden_layers_str):
        hidden_layers = ast.literal_eval(hidden_layers_str)

        if not (
            len(hidden_layers) > 2
                and isinstance(hidden_layers[-1], list)
                and isinstance(hidden_layers[-2], list)):
            raise ValueError('Invalid dueling network structure.')

        return\
            Models._remove_none_elements_from_list(hidden_layers[:-2]),\
            Models._remove_none_elements_from_list(hidden_layers[-2]),\
            Models._remove_none_elements_from_list(hidden_layers[-1])

    @staticmethod
    def _remove_none_elements_from_list(value_list):
        return [e for e in value_list if e is not None]
