#!/usr/bin/python3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = cythonize(
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
			"Robot.py",
			"RobotControlInput.py",
			"Shape.py",
			"StaticMapper.py",
			"Target.py"
		],
		language_level=3)

extensions.extend(cythonize(Extension("Vector", sources=["Vector.py", "c_src/_Vector.c"], include_dirs=[numpy.get_include()]), language_level=3));
extensions.extend(cythonize(Extension("Radar", sources=["Radar.py", "c_src/_Radar.c"], include_dirs=[numpy.get_include()]), language_level=3));

setup(
	name = "SafeNav Simulator",
	ext_modules = extensions
)

