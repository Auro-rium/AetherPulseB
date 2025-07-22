from fastapi import APIRouter, Depends
from app.utils.redis_client import redis_client
from app.db.connector import get_db
import json

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(db=Depends(get_db)):
    # Remove current_user dependency, make endpoint public
    # cache_key = f'dashboard:{current_user["_id"]}'
    # cached = redis_client.get(cache_key)
    # if cached:
    #     return json.loads(cached)
    # Fetch/process data from MongoDB
    # user_data = db["users"].find_one({"_id": current_user["_id"]})
    # data = {"user": user_data, "stats": "..."}  # Add your logic here
    # redis_client.setex(cache_key, 300, json.dumps(data))  # Cache for 5 min
    # return data
    # Instead, just return a placeholder or all users for now
    users = list(db["users"].find())
    for user in users:
        user["_id"] = str(user["_id"])
    return {"users": users, "stats": "..."}
