
Example03::

  '''
  Test server certificate validation against mail.google.com
  '''

  import ssl
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

  manager.add_cert_req(request.url, ssl.CERT_REQ)

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
