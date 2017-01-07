
SOURCES = Circle.py Distributions.py DynamicObstacles.py Environment.py Game.py Geometry.py Main.py Polygon.py Radar.py Robot.py Shape.py Target.py Vector.py

all: cython

cython: $(SOURCES) setup.py
	python3 setup.py build_ext --inplace

.PHONY: clean
clean:
	rm *.c *.so
	rm -r build __pycache__

