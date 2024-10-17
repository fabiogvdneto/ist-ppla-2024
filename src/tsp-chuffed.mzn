% Project - Test Scheduling Problem as a CSP

% Author: Fabio Neto (ist1104126)
% Problem Specification: https://www.csplib.org/Problems/prob073

% Each test has a given duration and needs to run on one machine.
% While the test is running on a machine, no other test can use
% that machine. Some tests can only be assigned to a subset of
% the machines, for others you can use any available machine. For
% some tests, additional, possibly more than one, global resources
% are needed. While those resources are used for a test, no other
% test can use them.


% The objective is to finish the set of all tests as quickly as
% possible, i.e. all start times should be non-negative, and
% makespan should be minimized. The makespan is the difference
% between the start of the earliest test, and the end of the
% latest finishing test.

include "globals.mzn";

% ------
%
%  Variables
%
% ------

int: T; % Number of tests.
int: M; % Number of machines.
int: R; % Number of resources.

array[tests] of        (1..):     test_duration;
array[tests] of set of resources: test_resources;
array[tests] of set of machines:  test_machines;

%
% ---/---
%

set of int: tests     = 1..T;
set of int: machines  = 1..M;
set of int: resources = 1..R;

% Resource dependents (tests).
array[resources] of set of tests: resource_dependents = [{t | t in tests where requires_r(t, r)} | r in resources];

% Minimum and maximum makespan.
int: min_makespan = max(r in resources)(sum([test_duration[t] | t in tests where requires_r(t, r)]));
int: max_makespan = max(m in machines )(sum([test_duration[t] | t in tests where requires_m(t, m)]));

%
% ---/---
%

array[tests] of var 0..max_makespan: test_start;
array[machines, tests] of var bool: schedule;

var min_makespan..max_makespan: makespan;

%
% ---/---
%

% Check if test t requires resource r.
function bool: requires_r(tests: t, resources: r)
	= r in test_resources[t];

% Check if test t requires machine m.
function bool: requires_m(tests: t, machines: m)
	= (card(test_machines[t]) = 0 \/ m in test_machines[t]);


% -------------
%
%  Constraints
%
% -------------

constraint::"calculate the makespan"
	forall(t in tests)(test_start[t] + test_duration[t] <= makespan);

constraint::"tests requiring the same global resource must not overlap in time"
	forall(tt in resource_dependents where card(tt) != 0)(
		disjunctive([test_start[t] | t in tt], [test_duration[t] | t in tt])
	);
	
constraint::"tests must be executed by 1 of the required machines"
	forall(t in tests, m in machines where not requires_m(t,m))(
		schedule[m,t] = 0
	);

constraint::"tests must be executed by exactly 1 machine"
	forall(t in tests)(
		sum(schedule[..,t]) = 1
	);

constraint::"tests running on the same machine must not overlap in time"
	forall(m in machines)(
		cumulative(test_start, test_duration, schedule[m,..], 1)
	);

% set of machines: non_symm_machines = array_union([ test_machines[t] | t in tests where card(test_machines[t]) < card(machines) ]);
% set of machines: symm_machines = machines diff non_symm_machines;

% constraint symmetry_breaking_constraint(
% 	lex_chain_less(schedule[symm_machines,..])
% );

% ----------
%
%  Solution
%
% ----------

solve :: seq_search([
			int_search([makespan], input_order, indomain_split),
			])
	minimize makespan;

output [
	  "Resrc: ", show(test_resources),
	"\nMachi: ", show(schedule),
	"\nStart: ", show(test_start),
	"\nDurat: ", show(test_duration),
	"\nMkspn: ", show(makespan)
];