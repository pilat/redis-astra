from astra import base_fields
from astra import validators


class CharField(validators.CharValidatorMixin, base_fields.BaseField):
    directly_redis_helpers = ('setex', 'setnx', 'append', 'bitcount',
                              'getbit', 'getrange', 'setbit', 'setrange',
                              'strlen', 'expire', 'ttl')


class BooleanField(validators.BooleanValidatorMixin, base_fields.BaseField):
    directly_redis_helpers = ('setex', 'setnx', 'expire', 'ttl',)


class IntegerField(validators.IntegerValidatorMixin, base_fields.BaseField):
    directly_redis_helpers = ('setex', 'setnx', 'incr', 'incrby', 'decr',
                              'decrby', 'getset', 'expire', 'ttl',)


class ForeignField(validators.ForeignObjectValidatorMixin,
                   base_fields.BaseField):
    def assign(self, value):
        if value is None:  # Remove field when None was passed
            self.db.delete(self.get_key_name())
        else:
            super(ForeignField, self).assign(value)

    def obtain(self):
        """
        Convert saved pk to target object
        """
        if not self._to:
            raise RuntimeError('Relation model is not loaded')
        value = super(ForeignField, self).obtain()
        return self._to_wrapper(value)


class ForeignKey(ForeignField):  # legacy alias
    pass

class DateField(validators.DateValidatorMixin, base_fields.BaseField):
    directly_redis_helpers = ('setex', 'setnx', 'expire', 'ttl',)


class DateTimeField(validators.DateTimeValidatorMixin, base_fields.BaseField):
    directly_redis_helpers = ('setex', 'setnx', 'expire', 'ttl',)


class EnumField(validators.EnumValidatorMixin, base_fields.BaseField):
    pass


# Hashes
class CharHash(validators.CharValidatorMixin, base_fields.BaseHash):
    pass


class BooleanHash(validators.BooleanValidatorMixin, base_fields.BaseHash):
    pass


class IntegerHash(validators.IntegerValidatorMixin, base_fields.BaseHash):
    pass


class DateHash(validators.DateValidatorMixin, base_fields.BaseHash):
    pass


class DateTimeHash(validators.DateTimeValidatorMixin, base_fields.BaseHash):
    pass


class EnumHash(validators.EnumValidatorMixin, base_fields.BaseHash):
    pass

class ForeignHash(validators.ForeignObjectValidatorMixin,
                  base_fields.BaseHash):
    def assign(self, value):
        if value is None:  # Remove hash key when None was passed
            super(ForeignHash, self).remove()
        else:
            super(ForeignHash, self).assign(value)

    def obtain(self):
        """
        Convert saved pk to target object
        """
        if not self._to:
            raise RuntimeError('Relation model is not loaded')
        value = super(ForeignHash, self).obtain()
        return self._to_wrapper(value)

class List(base_fields.BaseCollection):
    """
    :
    """
    field_type_name = 'list'

    _allowed_redis_methods = ('lindex', 'linsert', 'llen', 'lpop', 'lpush',
                              'lpushx', 'lrange', 'lrem', 'lset', 'ltrim',
                              'rpop', 'rpoplpush', 'rpush', 'rpushx',)
    _single_object_answered_redis_methods = ('lindex', 'lpop', 'rpop',)
    _list_answered_redis_methods = ('lrange',)

    def __len__(self):
        return self.llen()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.lrange(item.start, item.stop)
        else:
            ret = self.lrange(item, item)
            return ret[0] if len(ret) == 1 else None


class Set(base_fields.BaseCollection):
    field_type_name = 'set'
    _allowed_redis_methods = ('sadd', 'scard', 'sdiff', 'sdiffstore', 'sinter',
                              'sinterstore', 'sismember', 'smembers', 'smove',
                              'spop', 'srandmember', 'srem', 'sscan', 'sunion',
                              'sunionstore')
    _single_object_answered_redis_methods = ('spop',)
    _list_answered_redis_methods = ('sdiff', 'sinter', 'smembers',
                                    'srandmember', 'sscan', 'sunion',)

    def __len__(self):
        return self.scard()


class SortedSet(base_fields.BaseCollection):
    field_type_name = 'zset'
    _allowed_redis_methods = ('bzpopmax', 'bzpopmin', 'zadd', 'zcard', 
                              'zcount', 'zincrby', 'zinterstore', 'zlexcount',
                              'zrange', 'zpopmax', 'zpopmin', 'zrangebylex',
                              'zrangebyscore', 'zrank', 'zrem',
                              'zremrangebylex', 'zremrangebyrank',
                              'zremrangebyscore', 'zrevrange',
                              'zrevrangebylex', 'zrevrangebyscore', 'zrevrank',
                              'zscan', 'zscore', 'zunionstore')
    _single_object_answered_redis_methods = ()
    _list_answered_redis_methods = ('zpopmax', 'zpopmin', 'zrange',
                                    'zrangebylex', 'zrangebyscore',
                                    'zrevrange', 'zrevrangebylex',
                                    'zrevrangebyscore', 'zscan', )

    def __len__(self):
        return self.zcard()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.zrangebyscore(item.start or '-inf',
                                      item.stop or '+inf')
        else:
            ret = self.zrangebyscore(item, item)
            return ret[0] if len(ret) == 1 else None
