# Test Scheduling Problem

The [Test Scheduling Problem](https://www.csplib.org/Problems/prob073/)
(TSP) is a classical optimization problem that seeks to find the
shortest possible sequence of tests that can be performed on a
set of machines in order to minimize the total time required to
complete all tests. The problem was presented as the
Industrial Modelling Challenge at CP2015.

This project is a Python implementation of the TSP problem using
the MiniZinc language, a declarative language for specifying
and solving constraint satisfaction problems (CSPs).

## Description

For each input file, the program will write the solution to an output file.

The input file should contain the following information:
* Number of tests
* Number of machines
* Number of resources
* Duration of each test
* Required machines for each test
* Required resources for each test

The output file will then contain one optimal solution for
that instance. To ensure that the solution is valid and optimal,
you may want to run the `checker.py` program on the generated
output file. If the checker gives "Solution is valid" then
everything is okay with the solution

**Warning**: for instances with a large number of tests,
machines and resources, you may want to increase the timeout
value in the `proj.py` file in order to avoid timeouts on 
complex solutions. The timeout value is very useful to avoid
wasting time on possibly infeasible solutions. Machines with
a low processing power may also need a higher timeout value.

## Getting Started

### Prerequisites

Before running the program, make sure you have
[MiniZinc Python](https://github.com/MiniZinc/minizinc-python?tab=readme-ov-file#installation)
installed on your system.

> MiniZinc Python can be installed by running pip install minizinc.
> It requires MiniZinc 2.6+ and Python 3.8+ to be installed on the system.
> MiniZinc python expects the minizinc executable to be available on the
> executable path, the $PATH environmental variable, or in a default
> installation location.

### Usage

There are three executables provided in the project:

* `python proj.py <input-file> <output-file>`  
    The main program that invokes the MiniZinc solver in order to
    find a solution.
* `python checker.py <input-file> <output-file>`  
    A program that checks if the given solution is valid and optimal.
    If the checker gives "Solution is valid" then everything is okay
    with the solution
* `./test.sh <path-to-input>`  
    A shell script that runs the main program and validates the
    solution with the checker. It can also be used for batch
    processing of multiple instances on the same folder. The
    solutions for each instance are saved in the `out` folder.
