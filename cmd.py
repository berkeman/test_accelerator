import subprocess
import threading

""" Run system commands with timeout
"""
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.out = None

    def stringer(self, x):
        if x:
            return tuple(line.decode('utf-8') for line in x.splitlines())
        else:
            return ()

    def run_command(self, capture = True):
        self.process = subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        out,err = self.process.communicate()
        self.out = tuple(map(self.stringer, (out, err)))

    # set default timeout to 2 minutes
    def run(self, capture = False, timeout = 120):
        thread = threading.Thread(target=self.run_command, args=(capture,))
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.out

# '''basic test cases'''

# # run shell command without capture
# Command('pwd').run()
# # capture the output of a command
# date_time = Command('date').run(capture=True)
# print(date_time)
# # kill a command after timeout
# Command('echo "sleep 10 seconds"; sleep 10; echo "done"').run(timeout=2)
