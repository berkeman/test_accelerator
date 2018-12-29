import os
import subprocess
import threading

class Command(object):
	# Run shell commands with timeout
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.out = None

    def _stringer(self, x):
        if x:
            return tuple(line.decode('utf-8') for line in x.splitlines())
        else:
            return ()

    def run_command(self):
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = self.process.communicate()
        self.out = tuple(map(self._stringer, (out, err)))

    def run(self, timeout = 10):
        thread = threading.Thread(target=self.run_command)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.out


class Test:
	def __init__(self, path='./', configfile_template=None):
		self.ix = -1
		self.path = path
		self.current_testpath = None
		# read config
		with open(configfile_template, 'rt') as fh:
			conf = fh.read().split('\n')
			self.conf = [line for line in conf if line.startswith('py')]
		# re-create testdir
		# in the future, move existing testdir to timestamped dir
		if os.path.isdir(self.path):
			from shutil import rmtree
			rmtree(path)
		os.mkdir(path)

	def new(self, num_workdirs=3):
		# create new testdir + workdirs
		self.ix += 1
		self.current_testpath =(os.path.join(self.path, 'TEST' + str(self.ix)))
		os.mkdir(self.current_testpath)
		self.wdnames = tuple('wd' + str(x) for x in range(num_workdirs))
		for wd in self.wdnames:
			os.mkdir(os.path.join(self.current_testpath, wd))
		return self.wdnames

	def configure(self, defined_workdirs=None, target=None, sources=None, num_slices=3):
		conf = self.conf[:] # copy
		if isinstance(num_slices, int):
			num_slices = [num_slices] * len(defined_workdirs)
		else:
			assert len(num_slices) == len(defined_workdirs), 'expect either one int for all or one int for each.'
		for wd, slices in zip(defined_workdirs, num_slices):
			conf.insert(0, 'workdir=%s:%s:%d' % (wd, os.path.join(self.current_testpath, wd), slices))
		if target:
			conf.insert(-1, 'target_workdir=%s' % (target,))
		if sources:
			conf.insert(-1, 'source_workdirs=' + ','.join(sources))
		conf.insert(-1, 'logfilename=' + os.path.join(self.current_testpath, 'log.txt'))
		conf.insert(-1, 'method_directories=standard_methods')
		with open(os.path.join(self.current_testpath, 'test.conf'), 'wt') as fh:
			fh.write('\n'.join(conf))

	def run(self):
		print('Run ' + self.current_testpath)
		command = 'cd accelerator; exec ./daemon.py --conf=' + os.path.join(self.current_testpath, 'test.conf')
		out = Command(command).run(timeout=1)
		parsed = self._parse(out)
		self._save('stdout.txt', '\n'.join(out[0]))
		self._save('stderr.txt', '\n'.join(out[1]))
		return parsed, out

	def _save(self, fname, x):
		with open(os.path.join(self.current_testpath, fname), 'wt') as fh:
			fh.write(x)

	def _parse(self, data):
		from re import match, search
		created = []
		sources = []
		target = None
		for line in data[0]:
			if line.startswith('Create'):
				created.append(match('Create (..*)-slices.conf', line).group(1))
			elif 'TARGET' in line:
				assert target is None, 'target assigned twice!'
				target = search('TARGET\\x1b\[1m   (\w+):', line).group(1)
			elif 'SOURCE' in line:
				sources.append(search('SOURCE   (\w+):', line).group(1))
		serving = 'Serving' in '\n'.join(data[1])
		return dict(created=set(created) if created else None,
				sources=set(sources) if sources else None,
				target=target if target else None,
				serving=serving,)
