
Example01::

  '''
  Simple connection to a site
  '''

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


  httxmgr = HttxManager()
  httxreq = HttxRequest('http://www.gmail.com')
  httxresp = httxmgr.urlopen(httxreq)

  print httxresp.status
  print httxresp.headers
  # print httxresp.body
