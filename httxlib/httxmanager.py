#!/usr/bin/env python
# -*- coding: latin-1; py-indent-offset:4 -*-
################################################################################
# 
# This file is part of HttxLib
#
# HttxLib is an HTTP(s) Python library suited multithreaded/multidomain
# applications
#
# Copyright (C) 2010-2011 Daniel Rodriguez (aka Daniel Rodriksson)
# Copyright (C) 2011 Sensible Odds Ltd
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
Main connecting object L{HttxManager} implementation
'''

from httxbase import HttxBase
from httxnetlocation import HttxNetLocation
import httxoptions


class HttxManager(HttxBase):
    '''
    Main HttxLib Connecting object. The HttxManager is responsible for creating
    and managing a set of L{HttxNetLocation} (net locations) objects that will in
    turn hold the actual connections.

    The net location objects will be created on demand and kept in storage.
    A reference to active netlocations, (those with a pending L{getresponse}
    after a L{request}) will also be stored in a cache.

    @ivar options: The shared options for the connection(s)
    @type options: L{HttxOptions}
    '''

    def __init__(self, **kwargs):
        '''
        Constructor. It delegates construction to the base class
        HttxBase, except for the proxy that will be set specifically

        Setting the proxy ensures the initialization of the storage of
        netlocations and the cache of active netlocations

        @param kwargs: keywords arguments
        @see: L{HttxOptions}
        '''
        HttxBase.__init__(self, **kwargs)
        self.netlocations = dict()
        self.locationcache = dict()

        if httxoptions.proxydefaults:
            self.setproxydefaults()

        # The user may have enforced a private proxy for a particular protocol
        # not necessarily overriding all system proxies (or yes)
        if 'proxy' in kwargs:
            self.setproxy(kwargs['proxy'])


    def __deepcopy__(self, memo):
        '''
        Deepcopy support.

        @param memo: standard __deepcopy__ parameter to avoid circular references
        @type memo: dict
        @return: cloned object
        @rtype: L{HttxManager}
        @see L{clone}
        '''
        return self.clone()


    def clone(self, options=None, netLocations=True):
        '''
        Clone the object using the supplied options or a new set of options if
        given.

        An equivalente set of L{HttxNetLocation} net locations will be replicated

        A new set of options will separate the clone object from the original
        object, since they will no longer share cookies, user/password/realm
        combinations or https certificates

        @param options: options for the cloned object
        @type options: L{HttxOptions}
        @param netLocations: whether to clone the existing netlocations
        @type netLocations: bool
        @return: cloned object
        @rtype: L{HttxManager}
        '''
        if not options:
            options = self.options.clone()

        clone = self.__class__(options=options)

        # Replicate the existing set of netlocations
        if netLocations:
            with self.lock:
                for netlockey, netlocation in self.netlocations.iteritems():
                    clone.netlocations[netlockey] = netlocation.clone(options=options)

        return clone


    def setproxydefaults(self):
        '''
        Set the proxy options from OS defaults or environment variables if present using
        the functionality preset in urllib
        '''
        from urllib import getproxies
        from urlparse import urlsplit
        proxies = getproxies()

        # Windows will return the "https" proxy with an "https" scheme when all protocols
        # should be using the same proxy. But obviously the same netlocation is not
        # simultaneously listening for clean and encrypted connections
        http = proxies.get('http', None)
        if http is not None:
            https = proxies.get('https', None)
            if https is not None:
                httpparsed = urlsplit(http)
                httpsparsed = urlsplit(https)
                if httpparsed.netloc == httpparsed.netloc:
                    proxies['https'] = http

        self.setproxy(proxies)


    def setproxy(self, proxy=None):
        '''
        Set the proxy options by opening specific netlocations for http and/or https schemes
        The proxy can be different for http and https connections.

        The L{HttxNetLocation} net locations storage and cache of active net locations
        are initialized
        
        @param proxy: proxy servers. Dictionary with scheme:url pairs.
                      '*' or 'httx' as the scheme stands for both http and https
        @type proxy: dict
        '''
        with self.lock:
            self.netlocations = dict()
            self.locationcache = dict()

            if proxy:
                if '*' in proxy:
                    proxy = {'http': proxy['*'], 'https': proxy['*']}
                elif 'httpx' in proxy:
                    proxy = {'http': proxy['httpx'], 'https': proxy['httpx']}

                for scheme, url in proxy.iteritems():
                    self.netlocations[scheme] = HttxNetLocation(url, options=self.options)


    def _getnetlocation(self, httxreq):
        '''
        Internal interface to fetch the appropiate L{HttxNetLocation} net location object
        to use to issue a request as specified by httxreq

        @param httxreq: Request to be executed
        @type httxreq: L{HttxRequest}
        @return: httxnetlocation
        @rtype: L{HttxNetLocation}
        '''
        # Protected to avoid a change of proxy options
        with self.lock:
            if httxreq.scheme == 'http' and 'http' in self.netlocations:
                # http request and http proxy in place
                httxnetlocation = self.netlocations[httxreq.scheme]
            elif httxreq.scheme == 'https' and 'https' in self.netlocations:
                # https request and http proxy in place
                httxnetlocation = self.netlocations[httxreq.scheme]
                if self.options.httpsconnect:
                    # connect is requested. each "https netloc" must have its own httxnetlocation
                    # create a new netlocation with the original https proxy url
                    # or fetch and existing one for the netlocation
                    httxnetlocation = self.netlocations.setdefault(httxreq.netloc,
                                                                   HttxNetLocation(httxnetlocation.url,
                                                                                   options=self.options))
            else:
                # Regular direct connection
                httxnetlocation = self.netlocations.setdefault(httxreq.netloc,
                                                               HttxNetLocation(httxreq.get_full_url(),
                                                                               options=self.options))

        # netlocation fetched - it can be given to different threads because it is also thread-safe
        return httxnetlocation


    def request(self, httxreq):
        '''
        Send the L{HttxRequest} httxreq to the specified server inside the request
        
        @param httxreq: Request or url to be executed
        @type httxreq: L{HttxRequest} or url (string)
        @return: sock
        @rtype: opaque type for the caller (a Python sock)
        '''
        httxnetlocation = self._getnetlocation(httxreq)
        sock = httxnetlocation.request(httxreq)

        # Store the sock - location relationship in a dictionary
        with self.lock:
            self.locationcache[sock] = httxnetlocation

        return sock


    def getresponse(self, sock):
        '''
        Recover a L{HttxResponse} using a net location from the cache of
        active L{HttxNetLocation} net locations and calling its getresponse
        
        @param sock: The opaque type returned by L{request}
        @type sock: opaque (a Python sock)
        @return: response
        @rtype: L{HttxResponse} (compatible with httplib HTTPResponse)
        '''
        with self.lock:
            # Get net location out of the cache of active net locations
            httxnetlocation = self.locationcache.pop(sock)

        # get the actual response
        response = httxnetlocation.getresponse(sock)

        # Check if the response is active (authenticating or redirecting)
        if response.isactive():
            # The response is undergoing further network activity
            # Place it again (with the returned sock which may be new)
            # in the cache of active locations
            with self.lock:
                self.locationcache[response.sock] = httxnetlocation

        return response


