
C_SOURCES = c_src/_GridDataRadar.c c_src/_Vector.c
PXD_SOURCES = GridDataRadar.pxd Vector.pxd
PY_SOURCES = Circle.py Distributions.py DrawTool.py DynamicObstacles.py Environment.py Game.py Geometry.py GridDataEnvironment.py GridDataRadar.py Main.py MapModifier.py MDPAdapterSensor.py MovementPattern.py ObstaclePredictor.py Polygon.py Radar.py Robot.py RobotControlInput.py Shape.py StaticMapper.py StaticGeometricMaps.py Target.py Vector.py NavigationAlgorithm/*.py
DOXYGEN_CONFIG_FILE = doxygen.conf

default: cython

cython: $(PY_SOURCES) setup.py $(PXD_SOURCES) $(C_SOURCES)
	python3 setup.py build_ext --inplace

doc: doxygen

doxygen: $(SOURCES) $(DOXYGEN_CONFIG_FILE)
	doxygen $(DOXYGEN_CONFIG_FILE)

.PHONY: clean
clean:
	rm -f *.c *.so NavigationAlgorithm/*.c NavigationAlgorithm/*.so
	rm -rf build __pycache__

