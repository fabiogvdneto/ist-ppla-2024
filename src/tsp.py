from proj import vprint
from math import floor
from datetime import timedelta
from minizinc import Model, Solver, Instance, Result, Status


def new(mzn: str, solvertag: str) -> Instance:
    """
    Create a new instance of the MiniZinc model.
    """
    model  = Model(mzn)
    solver = Solver.lookup(solvertag)
    return Instance(solver, model)


def lowerbound(inst: Instance) -> int:
    """
    Compute the lowerbound (minimum makespan) by building
    a sequence of tests that require the same resource.
    """
    resources   = range(inst["R"])
    tests       = range(inst["T"])
    t_duration  = inst["test_duration"]
    t_resources = inst["test_resources"]
    return max([sum([t_duration[t] for t in tests if (r+1) in t_resources[t]]) for r in resources])


def upperbound(inst: Instance) -> int:
    """
    Compute the upperbound (maximum makespan) by building
    a sequence of tests that may use the same machine.
    """
    machines   = range(inst["M"])
    tests      = range(inst["T"])
    t_duration = inst["test_duration"]
    t_machines = [(inst["test_machines"][t] if len(inst["test_machines"][t]) else machines) for t in tests]
    return max([sum([t_duration[t] for t in tests if (m+1) in t_machines[t]]) for m in machines])


def search(inst: Instance, stimeout: int) -> Result:
    """
    Modified version of the binary search algorithm optimized
    to work with MiniZinc and minimization problems. A timeout
    is given to avoid wasting time on possibly infeasible solutions.
    """
    lowerb = lowerbound(inst)
    upperb = upperbound(inst)
    timeouts = 0
    solution = None
    
    inst["min_makespan"] = lowerb
    print(f"Makespan: [{lowerb},{upperb}]")

    while upperb > lowerb:
        with inst.branch() as branch:
            # Guess the makespan while trying to avoid timeouts.
            offset = (upperb - lowerb) / (2 + timeouts**2)
            target = floor(upperb - offset)

            branch["max_makespan"] = target
            result = branch.solve(timeout=timedelta(seconds=stimeout))

            match result.status:
                case Status.SATISFIED:
                    # Reduce the upperbound to find the optimal makespan.
                    # The result makespan may be smaller than the goal.
                    vprint("(+)", result["makespan"])
                    upperb   = result["makespan"]
                    solution = result
                case Status.UNSATISFIABLE:
                    # Increase the lowerbound to find the optimal makespan.
                    print("(-)", target)
                    lowerb = target + 1
                case Status.UNKNOWN:
                    # Status.UNKNOWN means that the solver timed out.
                    # Increase the lowerbound to avoid more timeouts.
                    print("($)", target)
                    lowerb = target + 1
                    timeouts += 1
                case _:
                    # This should not happen.
                    print("Error: unexpected model status.\n", result.status)
                    exit()
    
    # A solution was found!
    # The solution is optimal if no timeout occurred.
    print("(f)", upperb)
    return solution


#   ----------
#  ---- IO ----
#   ----------


def load(inst: Instance, path: str):
    """
    Load the instance data from the file denoted by the given path.
    """
    t_duration  = []  # Duration for each test.
    t_machines  = []  # Required machines for each test.
    t_resources = []  # Required resources for each test.

    def test(_, duration, machines, resources):
        t_duration .append(duration)
        t_machines .append({ int(m[1:]) for m in machines })
        t_resources.append({ int(r[1:]) for r in resources })
    
    with open(path, 'r') as file:
        # Parse the numbers of tests, machines and resources
        inst["T"] = int(file.readline().rsplit(":", maxsplit=1)[1])
        inst["M"] = int(file.readline().rsplit(":", maxsplit=1)[1])
        inst["R"] = int(file.readline().rsplit(":", maxsplit=1)[1])

        # Evaluate the remaining lines.
        for line in file:
            eval(line, {}, {'test': test})
        
    inst["test_duration"]  = t_duration
    inst["test_machines"]  = t_machines
    inst["test_resources"] = t_resources


def save(inst: Instance, result: Result, path: str):
    """
    Save the instance results to the file denoted by the given path.
    """
    t_resources = inst["test_resources"]
    t_machine = result["test_machine"]
    t_start   = result["test_start"]

    # Group test execution details by machine.
    executions = [[] for _ in range(0, inst["M"])]

    # t = test | m = machine | r = resource
    # 0 = indexed starting from 0 (python-style)
    # 1 = indexed starting from 1 (minizn-style)
    for t0 in range(0, inst["T"]):
        m0 = t_machine[t0] - 1

        if (len(t_resources[t0]) == 0):
            executions[m0].append((f"t{t0+1}", t_start[t0]))
        else:
            executions[m0].append((f"t{t0+1}", t_start[t0], [f"r{r1}" for r1 in t_resources[t0]]))
    
    lines = []
    
    for m0 in range(0, inst["M"]):
        x = executions[m0]

        # Sort the timetable by start time.
        x.sort(key=lambda x: x[1])
        # Create a new line to be written to the output.
        lines.append(f"machine( 'm{m0+1}', {len(x)}, {str(x).replace(" ", "")})")

    with open(path, 'w') as file:
        file.write(str(result.solution))
        file.writelines("\n".join(lines))