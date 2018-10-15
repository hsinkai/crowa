#!/package/python-2.7/bin/python

# APMA-nagios-plugin :: check_servicemix
#
#  check if servicemix process is running.
#

import subprocess
import os
import re

def is_running(process_name):
	cnt = 0
	sp = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
	for process in sp.stdout:
		if re.search(process_name, process):
			# Skip grep process_name
			if re.search("check_proc_andrestart", process):
				continue
			cnt += 1
			#return True
	return cnt

import sys
try:
	procChecked = sys.argv[1]
except:
	print "No argument processname"
	exit(1)

try:
	procRestart = sys.argv[2]
except:
	print "No restart process"
	procRestart = None


processCnt = is_running(procChecked)
if processCnt > 0:
	print "PROCS OK: %d processes contain substr '%s'.\n" % \
		(processCnt, procChecked)
	exit(0)
else:
	print "PROCS CRITICAL: No process contains substr '%s'.\n" % procChecked
	if procRestart is not None:
		print "Restart command:", procRestart
		os.system(procRestart)
	processCnt = is_running(procChecked)
	if processCnt > 0:
		print "PROCS OK after restart."
		exit(0)
	else:
		print "PROCS CRITICAL: No process contains substr '%s'.\n" % procChecked

	exit(1)


