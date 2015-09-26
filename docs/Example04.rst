
Example04::

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
