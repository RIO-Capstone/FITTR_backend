# FITTR_API/huey.py
from huey import RedisHuey

huey = RedisHuey('fittr_huey', host='localhost', port=6379, db=0, block=False)
