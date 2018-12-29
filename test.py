#!/usr/bin/env python3
import os

from testbench import Test

CONF = 'conf/test.conf'
PATH = '____test'
test = Test(path = os.path.join(os.getcwd(), PATH), configfile_template=CONF)

# define 0, 1; target 0; source 1; => create 0, 1
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0], sources=wds[1:])
parsed, output = test.run()
assert parsed['serving'] and parsed['created'] == set(wds) and parsed['target'] == wds[0] and parsed['sources'] == {wds[1]}

# define 0, 1; target 0; => create 0
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0])
parsed, output = test.run()
assert parsed['serving'] and parsed['created'] == {wds[0]} and parsed['target'] == wds[0] and parsed['sources'] is None

# define 0, 1; target 0; source 0; => create 0
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0], sources=wds[:1])
parsed, output = test.run()
assert parsed['serving'] and parsed['created'] == {wds[0]} and parsed['target'] == wds[0] and parsed['sources'] is None

# define 0, 1; target 0; source 0, 1; => create 0, 1; twist: uneven sliceno cause error
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0], sources=wds, num_slices=(3, 4))
parsed, output = test.run()
assert not parsed['serving'] and 'ERROR:  Not all workdirs have the same number of slices!' in output[0]

# define 0, 1; source 0, 1; twist: no target cause errors
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, sources=wds)
parsed, output = test.run()
assert not parsed['serving'] and '# Error in configfile, must specify target_workdir.' in output[0]

# define 0...7; target 0; source 0...3; => create 0...3; twist: only 0...3 should be created and 1...3 are sources, 4...7 should be ignored
wds = test.new(num_workdirs=8)
test.configure(defined_workdirs=wds, target=wds[0], sources=wds[:4])
parsed, output = test.run()
assert parsed['serving'] and parsed['created'] == set(wds[:4]) and parsed['target'] == wds[0] and parsed['sources'] == set(wds[1:4])

# define 0, 1; target=dummy; twist: target does not exist
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target='dummy')
parsed, output = test.run()
assert not parsed['serving'] and 'ERROR:  Workdir(s) missing definition: "dummy".' in output[0]

# define 0, 1; target=0; sources=dummy; twist: source does not exist
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0], sources=['dummy',])
parsed, output = test.run()
assert not parsed['serving'] and 'ERROR:  Workdir(s) missing definition: "dummy".' in output[0]
