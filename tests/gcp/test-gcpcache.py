import unittest
import time

from cloudaux.gcp.gcpcache import GCPCache

class TestConnectionCache(unittest.TestCase):

    def test_get(self):
        myobj = object()
        c = GCPCache()

        key = 'strkey'
        self.assertTrue(c.insert(key, myobj))

        actualobj = c.get(key)
        self.assertEqual(myobj, actualobj)

    def test_get_expired(self):
        myobj = object()
        c = GCPCache()
        # Check that an object is expired.  Should return none
        key = 'strkey'
        exp_minutes = .000001
        self.assertTrue(c.insert(key, myobj,
                                 future_expiration_minutes=exp_minutes))

        # sleep for two seconds to ensure the client is expired.
        time.sleep(2)
        self.assertFalse(c.get(key))
        
        # delete_if_expired is True, so it should have been removed.
        self.assertTrue(key not in c._CACHE)

    def test_delete(self):
        myobj = object()
        c = GCPCache()
        key = 'strkey'
        self.assertTrue(c.insert(key, myobj))

        self.assertTrue(c.delete(key))

        # Verify that it is not present
        self.assertTrue(key not in c._CACHE)

if __name__ == '__main__':
    unittest.main()
