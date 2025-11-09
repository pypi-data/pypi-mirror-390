import os
import sys
import logging
from agora_config import config
from agora_logging import logger
import redis as REDIS
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff
import fakeredis

class RedisClientSingleton(): 
    '''
    Basic wrapper to unify how the connection to Redis is declared/configured.
    '''
    _instance: object
    """
    Connects to the Redis Server from Agora Core    
    """
    def __new__(cls, *args, **kwargs):
        cls.connect()
        return cls._instance

    def __init__(self):        
        self.connect_attempted = False
        pass   
      
    @staticmethod
    def connect():
        '''
        Connects to Redis
        
        Use 'AEA2:RedisClient:Server' to set the server address (default = 'redis').
        Use 'AEA2:RedisClient:Port' to set the port (default = 6379).
        
        When running on gateway, the default values are appropriate.
        '''
        mocking_redis = config["AEA2:RedisClient"] is None or config["AEA2:RedisClient"] == '' or config["AEA2:RedisClient:Mock"] == 'True'
        if mocking_redis:
            logger.info(f"faking Redis")
            RedisClientSingleton._instance = fakeredis.FakeRedis()
        else:
            serverUrl = os.getenv("REDIS_ADDRESS")
            if not serverUrl:
                server = config["AEA2:RedisClient:Server"].strip()
                if server == "":
                    logger.info(f"AEA2:RedisClient:Server not set - mocking redis client")
                    server = "alpine-redis"

                port = config["AEA2:RedisClient:Port"].strip()
                if port == "":
                    logger.info(f"AEA2:RedisClient:Port not set - mocking redis client")
                    port = "6379"
            else:
                serverUrl.strip()
                server = str.split(serverUrl, ":")[0]
                port = str.split(serverUrl, ":")[1]        
            
            # connect to redis
            RedisClientSingleton.doConnect(server, port)            
        
        if RedisClientSingleton.is_connected():
            logger.info("redis_client connected")
    
    @staticmethod
    def doConnect(server:str, port:str):
        logger.info(f"redis_client attempting connection to '{server}:{port}'")
        RedisClientSingleton._instance = REDIS.Redis(host=server, 
                                                     port=port, 
                                                     decode_responses=True, 
                                                     socket_keepalive=True,
                                                     retry=Retry(ExponentialBackoff(cap=10, base=1), 25), 
                                                     retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError], 
                                                     health_check_interval=1)
        if not RedisClientSingleton.is_connected():
            logger.info(f"failed to ping Redis server at '{server}:{port}', retrying") 
            raise REDIS.ConnectionError("failed to ping Redis server, retrying")
        RedisClientSingleton._instance.config_set('notify-keyspace-events', 'KEA')

    @staticmethod
    def is_connected():
        '''Returns 'True' if connected to Redis.'''
        mocking = config["AEA2:RedisClient"] is None or config["AEA2:RedisClient"] == '' or config["AEA2:RedisClient:Mock"] == 'True'
        if mocking:
            return True
        if RedisClientSingleton._instance.ping():
            return True
        return False

_redis_client = RedisClientSingleton()

redis = RedisClientSingleton._instance
