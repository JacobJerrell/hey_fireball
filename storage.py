# -*- coding: utf-8 -*-
"""
This module encapsulates interations with a storage mechanism
that holds informatoin such as user scores, remaining points
for user, etc.

The abstract class `Storage` defines the methods needed 
to interact with a storage mechanism. 

This module contains two `Storage` subclasses: redis and
inmemory. Additional subclasses can be made that allow 
the use of any appropriate storage mechanism (database,
flat-file, etc.)
"""
import os

try:
    import redis
except ImportError:
    redis = None


#####################
# API
#####################


class Storage():
    """Class that defines how module storage functions 
    interact with a storage provider.
    """
    def user_exists(self, user_id: str):
        """Return True if user_id is in storage."""
        pass

    def get_user_points_used(self, user_id: str):
        """Return number of points used or 0."""
        pass

    def add_user_points_used(self, user_id: str, num: int):
        """Add `num` to user's total used points.""" 
        pass

    def get_user_points_received(self, user_id: str):
        """Return number of points received or 0."""
        pass

    def add_user_points_received(self, user_id: str, num: int):
        """Add `num` to user's total received points."""
        pass

    def get_users_and_scores(self):
        """Return list of tuples (user_id, points_received)."""
        pass


class RedisStorage(Storage):
    """Implementation of `Storage` that uses Redis.
    
    Redis server's URL should be in env var `REDIS_URL`.

    key: username
    value: hash(POINTS_USED, POINTS_RECEIVED)
    """

    POINTS_USED = 'POINTS_USED'
    POINTS_RECEIVED = 'POINTS_RECEIVED'
    USERS_LIST_KEY = 'USERS_LIST'

    def __init__(self):
        super().__init__()
        # Check is Redis library is installed.
        if redis is None:
            raise Exception('Redis package not installed!')
        self._redis = redis.from_url(os.environ.get("REDIS_URL"))
        
    def _create_user_entry(self, user_id: str):
        """Create new user entry and init fields."""
        self._redis.hmset(user_id, {self.POINTS_USED:0, self.POINTS_RECEIVED:0})
        self._redis.sadd(self.USERS_LIST_KEY, user_id)

    def user_exists(self, user_id: str):
        """Return True if user_id is in storage."""
        return self._redis.exists(user_id)

    def get_user_points_used(self, user_id: str):
        """Return number of points used or 0."""
        return int(self._redis.hget(user_id, self.POINTS_USED))

    def add_user_points_used(self, user_id: str, num: int):
        """Add `num` to user's total used points."""
        self._redis.hincrby(user_id, self.POINTS_USED, num)

    def get_user_points_received(self, user_id: str):
        """Return number of points received or 0."""
        return int(self._redis.hget(user_id, self.POINTS_RECEIVED))

    def add_user_points_received(self, user_id: str, num: int):
        """Add `num` to user's total received points."""
        self._redis.hincrby(user_id, self.POINTS_RECEIVED, num)

    def get_users_and_scores(self):
        """Return list of tuples (user_id, points_received)."""
        users = self._redis.smembers(self.USERS_LIST_KEY)
        return [(user, self.get_user_points_received(user)) for user in users]


class InMemoryStorage(Storage):
    """Implementation of `Storage` that uses a dict in memory.
    """

    POINTS_USED = 'POINTS_USED'
    POINTS_RECEIVED = 'POINTS_RECEIVED'

    def __init__(self):
        super().__init__()
        # Check is Redis library is installed.
        self._data = dict()

    def user_exists(self, user_id: str):
        """Return True if user_id is in storage."""
        return user_id in self._data

    def get_user_points_used(self, user_id: str):
        """Return number of points used or 0."""
        return self._data[user_id].get(self.POINTS_USED, 0)

    def add_user_points_used(self, user_id: str, num: int):
        """Add `num` to user's total used points."""
        user_data = self._data.setdefault(user_id, {})
        user_data[self.POINTS_USED] = user_data.get(self.POINTS_USED, 0) + num

    def get_user_points_received(self, user_id: str):
        """Return number of points received or 0."""
        return self._data[user_id].get(self.POINTS_RECEIVED, 0)

    def add_user_points_received(self, user_id: str, num: int):
        """Add `num` to user's total received points."""
        user_data = self._data.setdefault(user_id, {})
        user_data[self.POINTS_RECEIVED] = user_data.get(self.POINTS_RECEIVED, 0) + num

    def get_users_and_scores(self):
        """Return list of tuples (user_id, points_received)."""
        return [(k, v[self.POINTS_RECEIVED]) for k,v in self._data.items()]