Requires Python >= 2.6.3/2.7.x

# Features #
  * HTTP/HTTPS
  * Proxy support (with and without CONNECT for HTTPS), supporting system defined proxies
  * Manual tunnel setup possible (CONNECT with no SSL for a pure binary connection)
  * Keepalive support
  * Compression support
  * Cookies support
  * Authentication (Proxy/User): Basic and Digest caching the answers for reuse
  * External Authentication handlers supported (to enable external handling of Negotiate, Kerberos, NTLM ...)
  * Username/Password for url/realm management
  * Client Certificates and Server Certificate Validation
  * Certificates, private keys and validation requirement management
  * Multithreading support
  * Redirection (with control for Internal/External Redirection and redirection depth)

=Documentation
  * The library reference online at PyPi: http://packages.python.org/HttxLib
  * Some examples in the Wiki: http://code.google.com/p/httxlib/wiki

# Why another Python HTTP library? #

Working on a project that was using suds (a Python SOAP client) I faced urllib2 for the first time only to be surprised by two facts:
  * No support for compressed answers
  * No support for keepalive connections
  * The usage pattern was (for the author) awkward: plug-in a handler for basic auth ... forcing the developer to know in advance which handlers to plug-in

In the search for a library that would support such things and also work fine from a multithreaded point of view, the following alternatives were seen:
  * httplib: Low level basic request/getresponse with keepalive support.
  * urllib3: A quick hack rather than a library on top of httplib to quicly reuse connections (it seemed abandoned back in 2010, but has been resurrected in 2011)
  * httplib2: The best alternative with keepalive connections, compression support, authentication, redirection. But **no support for cookies**. And setting options for the http objects are limited to a set of globals in the module. The usage pattern was also not comfortable.

The question was wether to extend httplib2 or work on something else. And the decision was clear: **work on something else** because I wanted to try a new design.

# Is the library ready? #

The library is in constant use in BfPy (http://code.google.com/p/bfpy) in non-public projects and in Bfplusplus (http://code.google.com/p/bfpy), so yes: **it is ready**

# The HttxLib library #

The idea was clear:

  * Reusing Python components as much as possible
  * Multithread support from the very beginning
  * Keep-alive, compression, authentication, redirection, proxy support and **cookies**
  * Request should be made by passing an object. If httplib and others are returning objects as responses, it was obvious that they should base the requests on objects too.

## The basic design ##

It is based around two concepts:
  * Hierarchy of objects: Overall Manager, Net Location Manager and Connection Manager
  * Domains of options. Enable easy sharing of options between objects

The first concept was solved by creating the aforementioned 3 sets of connecting objects with a common API(a connecting object is one that "can connect" to a host or at least make the user believe that it is establishing the connection, whilst delegating it to a lower level connecting object): urlopen (supported by a pair of request, getresponse functions that may also be used independently)

The 3 objects are:

  * HttxManager. Usually the only one to use. It handles simultaneously connections to different net locations (host:port combination)

  * HttxNetLocation. It handles multiple individual connections to a "net location" (host:port). Same interface. Once instantiated it handles multiple connections to the given "net location". Another "net location" needs another object.

  * HttxConnection. It handles individual connections (and authentication and redirection) to a specific netlocation. It uses httplib as the underlying transport mechanism

All these levels and connecting objects (imagine a scenario with 1 HttxManager, 4 HttxNetLocations and 10 HttxConnections per netlocation, totalling 40 individual connections in just one HttxManager) share a domain of options.

The domain of options controls things like:

  * Redirection, external redirectio and maximum number of redirections
  * Authentication and credentials for authentication
  * Compression and compression methods
  * Certificates and certificate validation
  * Etc ..

Once you have a manager you may chose to instantiate new ones. There are two possibilities:

  * Create it and pass the "options" of an existing one. The 2 managers will share the options and any change made to them (ex: disabling redirection support)
  * Create it. The options of the managers will remain isolated from each other.

A reference to the domain of options is passed to new connecting objects on creation, which allows to control the behaviour of the whole lot (40 connections in our case) with just one central location of options.

The domain of options can also be shared between 2 or more HttxManagers, if wished (for example to let each HttxManager connect to only 4 netlocations and have a maximum of 10 individual connections). And a HttxManager state can be cloned with a new domain of options to separate it from the original HttxManager

# Building blocks in the implementation #

As expressed above, one of the objectives was to reuse as many existing standard Python components as possible. This seemed plausible, given that:

  * urllib2 already has a fully functional CookieJar object to store and retrieve cookies
  * urllib2 already has fully functional password managers on a per realm/url basis
  * httplib is a very good library

The implementation therefore used the following pieces:

  * A subclass of urllib2 Request to implement HttxRequest
  * A extended version of httplib HTTPResponse to implement HttxResponse
  * Both httplib (request/getresponse) and urllib2 (urlopen) interfaces to work
  * New exceptions derive from HTTPException
  * HTTPPasswordRealmWithDefaultRealm was used to implement credential storage and storage of https certificate related parameters
  * Digest authentication code from httplib, reworked to make it more generic and cache-friendly
  * A subclass of httplib.HTTPSConnection to enable server certificate validation

# Examples #

See the wiki
  * http://code.google.com/p/httxlib/wiki/Example01
  * http://code.google.com/p/httxlib/wiki/Example02
  * http://code.google.com/p/httxlib/wiki/Example03
  * http://code.google.com/p/httxlib/wiki/Example04
  * http://code.google.com/p/httxlib/wiki/Example05

```
from httxlib import *

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

print
print '--->Disabling External Redirection<---'
manager.options.externalredirect = False

# An exception should happen now
try:
    response = manager.urlopen(request)
except RedirectError, e:
    print "Exception"
    print e.response.status
    print e.response.headers
    # print response.body
```

More examples are available in the source code (documented using Epydoc)