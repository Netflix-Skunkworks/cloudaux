"""
.. module: cloudaux.gcp.gcpcache
    :platform: Unix
    :copyright: (c) 2016 by Google Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Tom Melendez (@supertom) <supertom@google.com>
"""
import dateutil.tz
import datetime

class GCPCache(object):
    def __init__(self):
        self._CACHE = {}
        self._CACHE_STATS = {'access_stats': {}}

    def get(self, key, delete_if_expired=True):
        """
        Retrieve key from Cache.

        :param key: key to look up in cache.
        :type key: ``object``

        :param delete_if_expired: remove value from cache if it is expired.
                                  Default is True.
        :type delete_if_expired: ``bool``

        :returns: value from cache or None
        :rtype: varies or None
        """
        self._update_cache_stats(key, None)

        if key in self._CACHE:
            (expiration, obj) = self._CACHE[key]
            if expiration > self._now():
                self._update_cache_stats(key, 'hit')
                return obj
            else:
                if delete_if_expired:
                    self.delete(key)
                    self._update_cache_stats(key, 'expired')
                    return None
    
        self._update_cache_stats(key, 'miss')
        return None
        
    def insert(self, key, obj, future_expiration_minutes=15):
        """
        Insert item into cache.

        :param key: key to look up in cache.
        :type key: ``object``

        :param obj: item to store in cache.
        :type obj: varies

        :param future_expiration_minutes: number of minutes item is valid
        :type param: ``int``

        :returns: True
        :rtype: ``bool``
        """
        expiration_time = self._calculate_expiration(future_expiration_minutes)
        self._CACHE[key] = (expiration_time, obj)
        return True

    def delete(self, key):
        del self._CACHE[key]
        return True

    def _now(self):
        return datetime.datetime.now(dateutil.tz.tzutc())

    def _calculate_expiration(self, future_expiration_minutes=15):
        return self._now() + datetime.timedelta(
                minutes=future_expiration_minutes)

    def _update_cache_stats(self, key, result):
        """
        Update the cache stats.
        
        If no cache-result is specified, we iniitialize the key.
        Otherwise, we increment the correct cache-result.

        Note the behavior for expired.  A client can be expired and the key
        still exists.
        """
        if result is None:
            self._CACHE_STATS['access_stats'].setdefault(key,
                                         {'hit': 0, 'miss': 0, 'expired': 0})
        else:
            self._CACHE_STATS['access_stats'][key][result] +=1        
    
    def get_access_details(self, key=None):
        """Get access details in cache."""
        if key in self._CACHE_STATS:
            return self._CACHE_STATS['access_stats'][key]
        else:
            return self._CACHE_STATS['access_stats']

    def get_stats(self):
        """Get general stats for the cache."""
        expired = sum([x['expired'] for _, x in
                       self._CACHE_STATS['access_stats'].items()])
        miss = sum([x['miss'] for _, x in
                    self._CACHE_STATS['access_stats'].items()])

        hit = sum([x['hit'] for _, x in
                       self._CACHE_STATS['access_stats'].items()])
        return {
            'totals': {
                'keys': len(self._CACHE_STATS['access_stats']),
                'expired': expired,
                'miss': miss,
                'hit': hit,
                }
        }
