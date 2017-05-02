from collections import defaultdict


class FlagRegistry:
    r = defaultdict(list)

    @classmethod
    def register(cls, flag, depends_on=0, key=None):
        """
        optional methods must register their flag with the FlagRegistry.

        The registry:
            - stores the flags relevant to each method.
            - methods may be a dependent of other methods.
            - stores the dictionary key the return value will be saved as.
            - for methods with multiple return values, stores the flag/key for each return value.

        Single Return Value Example:
        ----------------------------

        @FlagRegistry.register(flag=FLAGS.LIFECYCLE, key='lifecycle_rules')
        def get_lifecycle(bucket_name, **conn):
            pass

        In this example, the `get_lifecycle` method will be called when the `LIFECYCLE` flag is set.
        The return value will be appended to the results dictionary with the 'lifecycle_rules' key.

        Multiple Return Value Example:
        ------------------------------

        @FlagRegistry.register(
            flag=(FLAGS.GRANTS, FLAGS.GRANT_REFERENCES, FLAGS.OWNER),
            key=('grants', 'grant_references', 'owner'))
        def get_grants(bucket_name, include_owner=True, **conn):
            pass

        In this example, the `get_grants` method will be called when the `GRANTS`, `GRANT_REFERENCES`, or `OWNER` flags are set.
        The return values will be appended to the results dictionary with the corresponding 'grants', 'grant_references', 'owner' key.

        Dependency Example:
        -------------------

        @ALBFlagRegistry.register(flag=FLAGS.LISTENERS, key='listeners')
        def get_listeners(alb, **conn):
            return describe_listeners(load_balancer_arn=alb['Arn'], **conn)


        @ALBFlagRegistry.register(flag=FLAGS.RULES, depends_on=FLAGS.LISTENERS, key='rules')
        def get_rules(alb, **conn):
            rules = list()
            for listener in alb['listeners']:
                rules.append(describe_rules(listener_arn=listener['ListenerArn'], **conn))
            return rules

        In this example, `get_rules` requires the listener ARNs which are obtained by calling `get_listeners`.  So, `get_rules`
        depends on `get_listeners`.  The `alb` object passed into `get_rules` will have already been mutated by `get_listeners`
        so it can iterate over the values in alb['listeners'] to extract the information it needs.

        The `get_rules` method does not itself mutate the alb object, but it instead returns a new object (`rules`) which is
        appended to the final return value by the FlagRegistry.
        """
        def decorator(fn):
            flag_list = flag
            key_list = key
            if type(flag) not in [list, tuple]:
                flag_list = [flag] 
            if type(key) not in [list, tuple]: 
                key_list = [key]
            for idx in xrange(len(flag_list)):
                cls.r[fn].append(
                    dict(flag=flag_list[idx],
                         depends_on=depends_on,
                         key=key_list[idx],
                         rtv_ix=idx))
            return fn
        return decorator

    @classmethod
    def _validate_flags(cls, flags):
        """
        Iterate over the methods to make sure we set the flag for any
        dependencies if the dependent is set.

        Example: ALB.RULES depends on ALB.LISTENERS, but flags does not have ALB.LISTENERS set.
        We will modify flags to make sure ALB.LISTENERS is set.

        :param flags:  The flags passed into `build_out()`.
        :return flags: Same as the argument by the same name, but potentially modified
        to have any dependencies.
        """
        for method, entries in cls.r.items():
            method_flag, _ = cls._get_method_flag(method)

            if not flags & method_flag:
                continue

            for entry in entries:
                if not flags & entry['depends_on']:
                    flags = flags | entry['depends_on']

        return flags

    @classmethod
    def _get_method_flag(cls, method):
        """
        Helper method to return the method flag and the flag of any dependencies.

        As a method may have multiple return values, each with their own flags, the method
        flag will be the combination (logical OR) of each.

        :param method: Must be a @FlagRegistry.register() decorated method.
        :return method_flag: Combination of all flags associated with this method.
        :return method_dependencies: Combination of all dependencies associated with this method.
        """
        method_flag = 0
        method_dependencies = 0

        for entry in cls.r[method]:
            method_flag = method_flag | entry['flag']
            method_dependencies = method_dependencies | entry['depends_on']
        return method_flag, method_dependencies

    @classmethod
    def _execute_method(cls, method, method_flag, method_dependencies, executed_flag, result, flags, *args, **kwargs):
        """
        Executes a @FlagRegistry.register() decorated method.

        First checks the flags to see if the method is required.
        Next, checks if there are any dependent methods that have yet to be executed.
            If so, return False instead of executing.  We will try again on a later pass.
        Finally, execute the method and mutate the result dictionary to contain the results
        from each return value.

        :return True: If this method was either executed or should be removed from future passes.
        :return False: If this method could not be executed because of outstanding dependent methods. (Try again later)
        """
        if not flags & method_flag:
            # by returning True, we remove this method from the method_queue.
            return True

        # Check if all method dependencies have been executed.
        # If a method still has unexecuted dependencies, add the method to the queue.
        if method_dependencies and not (method_dependencies & executed_flag):
            return False

        # At least one of the return values is required. Call the method.
        retval = method(*args, **kwargs)

        for entry in cls.r[method]:
            if len(cls.r[method]) > 1:
                key_retval = retval[entry['rtv_ix']]
            else:
                key_retval = retval
            if flags & entry['flag']:
                if entry['key']:
                    result.update({entry['key']: key_retval})
                else:
                    result.update(key_retval)

        return True

    
    @classmethod
    def _do_method_pass(cls, method_queue, executed_flag, result, flags, *args, **kwargs):
        """
        Loop over available methods, executing those that are ready.
        - Raise an exception if we don't execute any methods on a given path. (circular dependency)

        :return next_method_queue: The list of methods to use for the next pass.
        :return executed_flag: Binary combination of all flags whose attached methods have been executed.
        """
        did_execute_method = False
        next_method_queue = list()

        for method in method_queue:
            method_flag, method_dependencies = cls._get_method_flag(method)
            if cls._execute_method(method, method_flag, method_dependencies, executed_flag, result, flags, *args, **kwargs):
                did_execute_method = True
                executed_flag = int(executed_flag | method_flag)
            else:
                next_method_queue.append(method)

        if not did_execute_method:
            raise Exception('Circular Dependency Error.')

        return next_method_queue, executed_flag


    @classmethod
    def build_out(cls, result, flags, *args, **kwargs):
        """
        Provided user-supplied flags, `build_out` will find the appropriate methods from the FlagRegistry
        and mutate the `result` dictionary.

        Stage 1: Set the flags for any dependencies if not already set.
        Stage 2: Repeatedly loop over available methods, executing those that are ready.
        - Break when we've executed all methods.
        - Break and error out if we don't execute any on a given pass.

        :param: result - Dictionary to put results into.
        :param: flags - User-supplied combination of FLAGS.  (ie. `flags = FLAGS.CORS | FLAGS.WEBSITE`)
        :param: *args - Passed on to the method registered in the FlagRegistry
        :param: **kwargs - Passed on to the method registered in the FlagRegistry
        :return None:  Mutates the results dictionary.
        """
        flags = cls._validate_flags(flags)

        method_queue = cls.r.keys()
        executed_flag = 0
        while len(method_queue) > 0:
            method_queue, executed_flag = cls._do_method_pass(method_queue, executed_flag, result, flags, *args, **kwargs)
        return


class Flags(object):
    def __init__(self, *flags):
        from collections import OrderedDict
        self.flags = OrderedDict()
        self._idx = 0
        for flag in flags:
            self.flags[flag] = 2**self._idx
            self._idx += 1
        self.flags['ALL'] = 2**self._idx-1
    
    def __getattr__(self, k):
        return self.flags[k]
    
    def __repr__(self):
        return str(self.flags)