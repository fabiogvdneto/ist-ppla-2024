% Number of tests                  : 10
% Number of machines               : 3
% Number of resources              : 1
test( 't1', 2, [], [])
test( 't2', 4, [], ['r1'])
test( 't3', 3, [], ['r1'])
test( 't4', 4, [], ['r1'])
test( 't5', 3, [], [])
test( 't6', 2, [], [])
test( 't7', 1, ['m1'], [])
test( 't8', 2, ['m2'], [])
test( 't9', 3, ['m3'], [])
test( 't10', 5, ['m1','m3'], [])