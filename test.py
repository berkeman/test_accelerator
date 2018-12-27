#!/usr/bin/env python3

from cmd import Command

import os

CONF = 'conf/test.conf'
PATH = os.path.join(os.getcwd(), '____testdir')



class Test:
	def __init__(self, path='./', configfile_template=CONF):
		self.ix = -1
		self.path = path
		self.current_testpath = None
		# read config
		with open(configfile_template, 'rt') as fh:
			conf = fh.read().split('\n')
			self.conf = [line for line in conf if line.startswith('py')]
		print(self.conf)
		# re-create testdir
		# in the future, move existing testdir to timestamped dir
		from shutil import rmtree
		if os.path.isdir(self.path):
			rmtree(path)
		os.mkdir(path)

	def new(self, num_workdirs=3):
		# create new testdir
		self.ix += 1
		self.current_testpath =(os.path.join(self.path, 'TEST' + str(self.ix)))
		os.mkdir(self.current_testpath)
		# create new workdirs
		self.wdnames = tuple('wd' + str(x) for x in range(num_workdirs))
		for wd in self.wdnames:
			os.mkdir(os.path.join(self.current_testpath, wd))
		return self.wdnames

	def configure(self, defined_workdirs=None, target=None, sources=None):
		conf = self.conf
		for wd in defined_workdirs:
			conf.insert(0, 'workdir=%s:%s:3' % (wd, os.path.join(self.current_testpath, wd),))
		if target:
			conf.insert(-1, 'target_workdir=%s' % (target,))
		if sources:
			conf.insert(-1, 'source_workdirs=' + ','.join(sources))

		conf.insert(-1, 'logfilename=' + os.path.join(self.current_testpath, 'log.txt'))
		conf.insert(-1, 'method_directories=standard_methods')
		with open(os.path.join(self.current_testpath, 'test.conf'), 'wt') as fh:
			fh.write('\n'.join(conf))

	def run(self):
		command = 'cd accelerator; exec ./daemon.py --conf=' + os.path.join(self.current_testpath, 'test.conf')
		stdout = Command(command).run(timeout=2)
		parsed = self._parse(stdout)
		return parsed, stdout

	def _parse(self,data):
		from re import match, search
		created = []
		sources = []
		target = None
		# if 'deathening' in ...
		for line in data[0]:
			if line.startswith('Create'):
				created.append(match('Create (..*)-slices.conf', line).group(1))
			elif 'TARGET' in line:
				assert target is None, 'target assigned twice!'
				target = search('TARGET\\x1b\[1m   (\w+):', line).group(1)
			elif 'SOURCE' in line:
				sources.append(search('SOURCE   (\w+):', line).group(1))
		return {'created': set(created), 'sources': set(sources), 'target': target}


test = Test(path = os.path.join(os.getcwd(), '____test'))

# create 0,1; target 0; source 1
wds = test.new(num_workdirs=2)
test.configure(defined_workdirs=wds, target=wds[0], sources=wds[1:])
parsed, output = test.run()
assert parsed['created'] == set(wds) and parsed['target'] == wds[0] and parsed['sources'] == {wds[1]}




exit()
