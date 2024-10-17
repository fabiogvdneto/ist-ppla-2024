import src.tsp as tsp

from sys import argv


# Path to the MiniZinc model file.
MZN = "./src/tsp-gecode.mzn"
# MiniZinc compatible CSP solver.
SOLVER = "gecode"
# Path to the input file.
INPUT  = argv[1]
# Path to the output file.
OUTPUT = argv[2]
# Number of seconds given to the solver to find a solution.
# Change this value according to your machine's processing power.
TIMEOUT = 8
# Whether or not to print every step of the search to the std output.
VERBOSE = True


def main():
    if (len(argv) < 3):
        print("Usage: python proj.py <input-file> <output-file>")
        exit()

    inst = tsp.new(MZN, SOLVER)


    try:
        tsp.load(inst, INPUT)
    except FileNotFoundError:
        print("Input file not found:", INPUT)
        exit()
    
    result = tsp.search(inst, TIMEOUT)
    
    if result == None:
        print("No solution was found")
        exit()

    try:
        tsp.save(inst, result, OUTPUT)
    except FileNotFoundError:
        print("Output file not found:", OUTPUT)
        exit()


# Only print if verbose flag is enabled.
vprint = print if VERBOSE else lambda *a, **k: None

if __name__ == "__main__":
    main()