
SOURCES = Circle.py Distributions.py DynamicObstacles.py Environment.py Game.py Geometry.py Main.py Radar.py Robot.py Shape.py Target.py Vector.py ObstaclePredictor.py NavigationAlgorithm/*.py
DOXYGEN_CONFIG_FILE = doxygen.conf

default: cython

cython: $(SOURCES) setup.py
	python3 setup.py build_ext --inplace

doc: doxygen

doxygen: $(SOURCES) $(DOXYGEN_CONFIG_FILE)
	doxygen $(DOXYGEN_CONFIG_FILE)

.PHONY: clean
clean:
	rm -f *.c *.so NavigationAlgorithm/*.c NavigationAlgorithm/*.so
	rm -rf build __pycache__

