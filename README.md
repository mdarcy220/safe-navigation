# Safe Navigation Robotics Project

This project aims to create an algorithm to allow safe, autonomous
navigation for a single robot in an unknown environment.

## Running the simulator

As this simulator has evolved, it has become more like a library with many
different features and types of simulation configurations available. The
`run_default.py` file serves as a basic template for setting up and running
a simulation.  You can simply `cd` into the directory you cloned this
repository to, then run:

```
python3 run_default.py --display-every-frame
```

This will run a basic simulation, similar to the original scenario this
simulator was made for. You can run with the `--help` flag to see the
command-line arguments available by default.

### Unit tests

There are some (but not many) unit tests available in the `testcode` module. These can be run with `python3 -m testcode.<test-file-name>`. For example, to run the geometry unit tests in `testcode/geometry_test.py`, you would use:
```
python3 -m testcode.geometry_test
```

## Contributing

Use tabs, never spaces. Spaces can break the Cython compilation. Also, use Unix line endings.

