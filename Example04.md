
```
#!/usr/bin/env python
# -*- coding: latin-1; py-indent-offset:4 -*-
################################################################################
# 
# This file is part of HttxLib
#
# HttxLib is an HTTP(s) Python library suited multithreaded/multidomain
# applications
# Copyright (C) 2010  Daniel Rodriguez (aka Daniel Rodriksson)
#
# You can learn more and contact the author at:
#
#    http://code.google.com/p/httxlib/
#
# HttxLib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HttxLib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HttxLib. If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
'''
Managers can share the same domain of options or can be in different domains
having different set of options
'''

import sys
import time

from httxlib import *

class flushfile(object):

    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()

sys.stdout = flushfile(sys.stdout)
sys.stderr = flushfile(sys.stderr)

manager = HttxManager()
request = HttxRequest('http://www.gmail.com')

# No exception should occur in this case
try:
    response = manager.urlopen(request)
except RedirectError, e:
    print "Exception"
    print e

print response.status
print response.headers
# print response.body

time.sleep(3)
print
print '--->Disabling External Redirection<---'
print

manager.options.externalredirect = False
# An exception should happen now
try:
    response = manager.urlopen(request)
except RedirectError, e:
    print "---> Exception <---"
    print e.response.status
    print e.response.headers
    # print response.body

print
print '--->Cloning the manager with a new domain of options<---'
print
manager2 = manager.clone()
manager2.options.externalredirect = True

time.sleep(3)
print
print '--->The new manager should be able to follow the redirection<---'
print

# No exception should occur in this case
try:
    response = manager2.urlopen(request)
except RedirectError, e:
    print "Exception"
    print e

print response.status
print response.headers
# print response.body

time.sleep(3)
print
print '--->The old manager should still be unable to follow the redirection<---'
print

# An exception should happen now
try:
    response = manager.urlopen(request)
except RedirectError, e:
    print "---> Exception <---"
    print e.response.status
    print e.response.headers
    # print response.body
```