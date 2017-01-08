#!/usr/bin/python3

from distutils.core import setup
from Cython.Build import cythonize

setup(
	name = "SafeNav Simulator",
	ext_modules = cythonize(["Distributions.py",
		"Shape.py",
		"Circle.py",
		"DynamicObstacles.py",
		"Environment.py",
		"Game.py",
		"Main.py",
		"Radar.py",
		"Geometry.py",
		"Robot.py",
		"Target.py",
		"Vector.py"
	])
)

