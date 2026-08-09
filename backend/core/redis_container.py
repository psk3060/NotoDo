class RedisContainer:
    def __init__(self):
        self.refresh = None  # db0
        self.ip = None       # db1
        self.token = None    # db4
        
redis_container = RedisContainer()