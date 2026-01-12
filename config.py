import redis


API_KEY = "test"
THIS_URL = "http://localhost:8080"

r = redis.Redis(host="redis", port=6379, decode_responses=True)
