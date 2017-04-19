from collections import defaultdict


class FlagRegistry:
    r = defaultdict(list)

    @classmethod
    def register(cls, flag, key):
        """
        optional methods must register their flag with the FlagRegistry.
        
        The registry:
            - stores the flags relevant to each method.
            - stores the dictionary key the return value will be saved as.
            - for methods with multiple return values, stores the flag/key for each return value.
        
        Single Return Value Example:
        
        @FlagRegistry.register(flag=FLAGS.LIFECYCLE, key='lifecycle_rules')
        def get_lifecycle(bucket_name, **conn):
            pass
            
        In this example, the `get_lifecycle` method will be called when the `LIFECYCLE` flag is set.
        The return value will be appended to the results dictionary with the 'lifecycle_rules' key.
        
        Multiple Return Value Example:
        
        @FlagRegistry.register(
            flag=(FLAGS.GRANTS, FLAGS.GRANT_REFERENCES, FLAGS.OWNER),
            key=('grants', 'grant_references', 'owner'))
        def get_grants(bucket_name, include_owner=True, **conn):
            pass
        
        In this example, the `get_grants` method will be called when the `GRANTS`, `GRANT_REFERENCES`, or `OWNER` flags are set.
        The return values will be appended to the results dictionary with the corresponding 'grants', 'grant_references', 'owner' key.
        """
        def decorator(fn):
            flag_list = flag
            key_list = key
            if type(flag) not in [list, tuple]:
                flag_list = [flag] 
            if type(key) not in [list, tuple]: 
                key_list = [key]
            for idx in xrange(len(flag_list)):
                cls.r[fn].append(dict(flag=flag_list[idx], key=key_list[idx], rtv_ix=idx))
            return fn
        return decorator
    
    @classmethod
    def build_out(cls, result, flags, *args, **kwargs):
        """
        Provided user-supplied flags, `build_out` will find the appropriate methods from the FlagRegistry
        and mutate the `result` dictionary.
        
        :param: result - Dictionary to put results into.
        :param: flags - User-supplied combination of FLAGS.  (ie. `flags = FLAGS.CORS | FLAGS.WEBSITE`)
        :param: *args - Passed on to the method registered in the FlagRegistry
        :param: **kwargs - Passed on to the method registered in the FlagRegistry
        :return: None.  Mutates the results dictionary.
        """
        for method, entries in cls.r.items():
            retval = method(*args, **kwargs)
            for entry in entries:
                if len(entries) > 1:
                    key_retval = retval[entry['rtv_ix']]
                else:
                    key_retval = retval
                if flags & entry['flag']:
                    result.update({entry['key']: key_retval})