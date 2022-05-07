

import multiprocessing
import subprocess
import time

import threading 


class SubProcess(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.rcode = None

    def run(self):
        print "run_cmd: %s" % self.cmd
        p = subprocess.Popen(self.cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        
        while True:
            if p.poll() is None:
                self.parse_output(p)
                self.rcode = p.returncode
                break
            
            self.parse_output(p)
            
            time.sleep(0.1)
            
        print "END: ", self.rcode
            
    def parse_output(self, p):
        o = []
        e = []
        
        while True:
            o_line = p.stdout.readline()
            e_line = p.stderr.readline()
                
            if not o_line and not e_line:
                break
            
            if o_line:
                o.append(o_line[:-1])
            if e_line:
                e.append(e_line[:-1])
            
        for _o in o:
            print "O: ", _o
        for _e in e:
            print "E: ", _e
    
    
class MProcess(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.rcode = None

    def run_cmd(self, cmd):
        pass
    
    def run(self):
        print "run_cmd: %s" % self.cmd
        
        p = multiprocessing.Process(target=run_cmd, args=(cmd,))
        
        while True:
            if not p.is_alive():
                self.parse_output()
                self.rcode = p.exitcode
                break
            
            self.parse_output()
            
            time.sleep(0.1)
            
    def parse_output(self):
        pass
        
        
    
def finished_cb():
    print "cb"   
    
    
     
def main():
    '''
    '''
    cmds = [
        '/usr/bin/python /usr/local/bin/pyflakes  /Users/xavier/PYTHON_TOOLS/pycodechecker/pyanalysers/PythonCodeAnalysersApp.py',
        '/usr/bin/python /usr/local/bin/pyflakes  /Users/xavier/PYTHON_TOOLS/pycodechecker/pyanalysers/PythonCodeAnalysersApp22.py',
        '/usr/bin/python /usr/local/bin/pyflakes  /Users/xavier/PYTHON_TOOLS/pycodechecker/pyanalysers/PythonCodeAnalysersApp.py',
    ]
    
    for cmd in cmds:
        try:
            process = SubProcess(cmd)
            process.start()
        except Exception, msg:
            print "error: %s" % str(msg)


if __name__ == '__main__':
    print "main"
    main()
    print "done"
  
    