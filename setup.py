#!/usr/bin/python3

from distutils.core import setup
from Cython.Build import cythonize

setup(
	name = "SafeNav Simulator",
	ext_modules = cythonize(
		module_list = [
			"Circle.py",
			"Distributions.py",
			"DynamicObstacles.py",
			"Environment.py",
			"Game.py",
			"Geometry.py",
			"Main.py",
			"NavigationAlgorithm/*.py",
			"ObstaclePredictor.py",
			"Radar.py",
			"Robot.py",
			"RobotControlInput.py",
			"Shape.py",
			"StaticMapper.py",
			"Target.py",
			"Vector.py"
		],
		language_level=3
	)
)

