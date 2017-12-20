#!/usr/bin/python3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = cythonize(
		module_list = [
			"Circle.py",
			"Distributions.py",
			"DrawTool.py",
			"DynamicObstacles.py",
			"Environment.py",
			"Game.py",
			"Geometry.py",
			"GridDataEnvironment.py",
			"Main.py",
			"MapModifier.py",
			"MDPAdapterSensor.py",
			"MovementPattern.py",
			"NavigationAlgorithm/*.py",
			"ObstaclePredictor.py",
			"Polygon.py",
			"Radar.py",
			"RobotControlInput.py",
			"Robot.py",
			"Shape.py",
			"StaticMapper.py",
			"Target.py",
		],
		language_level=3)

extensions.extend(cythonize(Extension("Vector", sources=["Vector.py", "c_src/_Vector.c"], include_dirs=[numpy.get_include()]), language_level=3));
extensions.extend(cythonize(Extension("GridDataRadar", sources=["GridDataRadar.py", "c_src/_GridDataRadar.c"], include_dirs=[numpy.get_include()]), language_level=3));

setup(
	name = "SafeNav Simulator",
	ext_modules = extensions
)

