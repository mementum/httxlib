#!/usr/bin/env python
# -*- coding: latin-1; py-indent-offset:4 -*-
################################################################################
# 
# This file is part of HttxLib
#
# HttxLib is an HTTP(s) Python library suited multithreaded/multidomain
# applications
#
# Copyright (C) 2010-2011  Daniel Rodriguez (aka Daniel Rodriksson)
# Copyright (C) 2011  Sensible Odds Ltd
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
No need to lock a manager in different threads

Locking happens in the background automatically
'''

import time
import threading
import sys

from httxlib import *

class flushfile(object):

    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()

sys.stdout = flushfile(sys.stdout)
sys.stderr = flushfile(sys.stderr)

def myFunc(myId, manager):

    request = HttxRequest('http://www.gmail.com')
    while True:
        response = manager.urlopen(request)
        print "my id: %d" % myId
        print response.status
        print response.headers
        time.sleep(3)

manager = HttxManager()

th1 = threading.Thread(target=myFunc, args=(1, manager))
th1.daemon = True
th2 = threading.Thread(target=myFunc, args=(2, manager))
th2.daemon = True
th3 = threading.Thread(target=myFunc, args=(3, manager))
th3.daemon = True

th1.start()
th2.start()
th3.start()

time.sleep(10)

sys.exit(0)



