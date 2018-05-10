
## @file util.py
#

## Constructs an algorithm from a config dict.
#
# The config looks something like:
#
#     {
#         "type": <name_of_algorithm_type>,
#         "params": {<dict_of_algorithm_parameters>}
#     }
#
# The `*args` and `**kwargs` are passed directly to the algorithm constructor. The
# `kwargs` argument *must not include "params"*, since this function will add a
# "params" field based on the `algo_config`.
#
def algo_from_config(algo_config, *args, **kwargs):
	algo_type = algo_config['type']

	if 'params' in kwargs:
		raise ValueError("kwargs MUST NOT contain \"params\", as it would be overwritten")

	kwargs['params'] = algo_config['params']

	constructor_func = None

	if algo_type == 'drrt':
		from .DynamicRrtNavAlgo import DynamicRrtNavigationAlgorithm
		constructor_func = DynamicRrtNavigationAlgorithm
	elif algo_type =='problp':
		from .SamplingNavAlgo import SamplingNavigationAlgorithm
		constructor_func = SamplingNavigationAlgorithm
	elif algo_type == 'global_local':
		from .GlobalLocalNavAlgo import GlobalLocalNavigationAlgorithm
		constructor_func = GlobalLocalNavigationAlgorithm
	elif algo_type == 'dwa':
		from .SamplingNavAlgo import DwaSamplingNavigationAlgorithm
		constructor_func = DwaSamplingNavigationAlgorithm
	elif algo_type == 'sfm':
		from .SFMNavAlgo import SFMNavigationAlgorithm
		constructor_func = SFMNavigationAlgorithm
	else:
		raise ValueError("Invalid algorithm type in config")


	return constructor_func(*args, **kwargs)


