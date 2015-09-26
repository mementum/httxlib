
Example02::

  '''
  www.gmail.com issues a redirection to mail.google.com, which is an external site

  Disabling redirection and external redirection can be tested
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

  time.sleep(3)
  print
  print '--->Disabling only redirection<---'
  print

  manager.options.externalredirect = True
  manager.options.redirect = False

  # An exception should happen now
  try:
      response = manager.urlopen(request)
  except RedirectError, e:
      print "---> Exception <---"
      print e.response.status
      print e.response.headers
      # print response.body
