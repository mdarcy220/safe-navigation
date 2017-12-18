# Safe Navigation Robotics Project

This project aims to create an algorithm to allow safe, autonomous
navigation for a single robot in an unknown environment.

## Running the simulator

To run the simulator, first `cd` into the directory you cloned this
repository to, then run:

```
python3 Main.py
```

There are many settings that can be configured from the command line. To
see which flags are available, just run:

```
python3 Main.py --help
```

### Unit tests

There are some (but not many) unit tests available in the `testcode` module. These can be run with `python3 -m testcode.<test-file-name>`. For example, to run the geometry unit tests in `testcode/geometry_test.py`, you would use:
```
python3 -m testcode.geometry_test
```

## Contributing

Use tabs, never spaces. Spaces break the Cython compilation. Also, use Unix line endings.

