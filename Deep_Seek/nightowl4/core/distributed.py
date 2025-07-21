import redis
import pickle
from datetime import datetime

class DistributedScanner:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.task_queue = "nightowl_tasks"
        self.result_queue = "nightowl_results"
    
    def enqueue_task(self, task_type, target, config=None):
        task = {
            "type": task_type,
            "target": target,
            "config": config or {},
            "timestamp": datetime.now().isoformat()
        }
        self.redis.rpush(self.task_queue, pickle.dumps(task))
        return True
    
    def get_task(self):
        task_data = self.redis.blpop(self.task_queue, timeout=30)
        if task_data:
            return pickle.loads(task_data[1])
        return None
    
    def send_result(self, task, result):
        result_data = {
            "task_id": task.get("timestamp"),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.redis.rpush(self.result_queue, pickle.dumps(result_data))
    
    def get_results(self, task_id):
        results = []
        while True:
            result_data = self.redis.lpop(self.result_queue)
            if not result_data:
                break
            result = pickle.loads(result_data)
            if result["task_id"] == task_id:
                results.append(result)
        return results