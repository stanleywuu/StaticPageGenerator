import os
import sys
import subprocess

if len(sys.argv) > 1:
 path = sys.argv[1]

p = subprocess.call('find ' + path + " -name *.html", shell=True)
(output, err) = p.communicate()


