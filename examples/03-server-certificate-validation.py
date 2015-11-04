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
Test server certificate validation against mail.google.com
'''

import ssl
import sys
import time

import httxlib
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
request = HttxRequest('https://mail.google.com')

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
print '--->Requesting server certificate validation<---'
print

manager.add_cert_req(request.get_full_url(), httxlib.CERT_REQUIRED)

#
# PLEASE PROVIDE A PATH TO A CERTIFICATE ROOT TO
# VERIFY the google server certificate
# YOU CAN FIND OUT WITH YOUR BROWSER WHO THE
# SIGNING AUTHORITY IS AND DOWNLOAD THEIR ROOT
# CERTIFICATE (use the pem format if in doubt)
#

# manager.add_ca_cert(request.url, path_to_file)

# An exception may happen if server validation fails
# or no root certificates are provided
try:
    response = manager.urlopen(request)
except RedirectError, e:
    print "---> Exception <---"
    print e
    # print e.response.status
    # print e.response.headers
    # print response.body
