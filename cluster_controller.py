from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import time

from utils import WorkerInfo

app = FastAPI()

class Controller:
    def __init__(self, dispatch_method: str = None):
        # Dict[str -> WorkerInfo]
        self.worker_info = {}
        # self.dispatch_method = DispatchMethod.from_str(dispatch_method)

        # self.heart_beat_thread = threading.Thread(
        #     target=heart_beat_controller, args=(self,)
        # )
        # self.heart_beat_thread.start()

    def register_worker(
        self, worker_name: str, check_heart_beat: bool, worker_status: dict
    ):
        if worker_name not in self.worker_info:
            print(f"Register a new worker: {worker_name}")
        else:
            print(f"Register an existing worker: {worker_name}")

        if not worker_status:
            worker_status = self.get_worker_status(worker_name)
        if not worker_status:
            return False

        self.worker_info[worker_name] = WorkerInfo(
            worker_status["model_names"],
            worker_status["speed"],
            worker_status["queue_length"],
            check_heart_beat,
            time.time(),
            extend_info=worker_status,
        )
        # 持久化更新到 Redis
        # rds.set(worker_info_key, serialize(self.worker_info))
        # logger.info(f"Register done: {worker_name}, {worker_status}")
        return True
    
    # def get_worker_status(self, worker_name: str):
    #     try:
    #         r = requests.post(worker_name + "/worker_get_status", timeout=5)
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"Get status fails: {worker_name}, {e}")
    #         return None

    #     if r.status_code != 200:
    #         logger.error(f"Get status fails: {worker_name}, {r}")
    #         return None

    #     return r.json()

    # def remove_worker(self, worker_name: str):
    #     logger.info("remove worker")
    #     del self.worker_info[worker_name]
    #     rds.set(worker_info_key, serialize(self.worker_info))

    # def list_models(self):
    #     models = dict()

    #     for w_name, w_info in self.worker_info.items():
    #         for name in w_info.model_names:
    #             if name not in models:
    #                 models[name] = {'worker_num': 0}
    #             models[name]['worker_num'] += 1
    #             models[name][models[name]['worker_num']] = w_info

    #     return models

    # def get_worker_address(self, model_name: str):
    #     if self.dispatch_method == DispatchMethod.LOTTERY:
    #         worker_names = []
    #         worker_speeds = []
    #         for w_name, w_info in self.worker_info.items():
    #             if model_name in w_info.model_names:
    #                 worker_names.append(w_name)
    #                 worker_speeds.append(w_info.speed)
    #         worker_speeds = np.array(worker_speeds, dtype=np.float32)
    #         norm = np.sum(worker_speeds)
    #         if norm < 1e-4:
    #             return ""
    #         worker_speeds = worker_speeds / norm
    #         if True:  # Directly return address
    #             pt = np.random.choice(np.arange(len(worker_names)), p=worker_speeds)
    #             worker_name = worker_names[pt]
    #             return worker_name

    #         # Check status before returning
    #         while True:
    #             pt = np.random.choice(np.arange(len(worker_names)), p=worker_speeds)
    #             worker_name = worker_names[pt]

    #             if self.get_worker_status(worker_name):
    #                 break
    #             else:
    #                 self.remove_worker(worker_name)
    #                 worker_speeds[pt] = 0
    #                 norm = np.sum(worker_speeds)
    #                 if norm < 1e-4:
    #                     return ""
    #                 worker_speeds = worker_speeds / norm
    #                 continue
    #         return worker_name
    #     elif self.dispatch_method == DispatchMethod.SHORTEST_QUEUE:
    #         worker_names = []
    #         worker_qlen = []
    #         for w_name, w_info in self.worker_info.items():
    #             if model_name in w_info.model_names:
    #                 worker_names.append(w_name)
    #                 worker_qlen.append(w_info.queue_length / w_info.speed)
    #         if len(worker_names) == 0:
    #             return ""
    #         min_index = np.argmin(worker_qlen)
    #         w_name = worker_names[min_index]
    #         self.worker_info[w_name].queue_length += 1
    #         logger.info(
    #             f"names: {worker_names}, queue_lens: {worker_qlen}, ret: {w_name}"
    #         )
    #         rds.set(worker_info_key, serialize(controller.worker_info))
    #         return w_name
    #     else:
    #         raise ValueError(f"Invalid dispatch method: {self.dispatch_method}")

    # def receive_heart_beat(self, worker_name: str, queue_length: int):
    #     if worker_name not in self.worker_info:
    #         logger.info(f"Receive unknown heart beat. {worker_name}")
    #         return False

    #     self.worker_info[worker_name].queue_length = queue_length
    #     self.worker_info[worker_name].last_heart_beat = time.time()
        
    #     rds.set(worker_info_key, serialize(self.worker_info))
    #     logger.info(f"Receive heart beat. {worker_name}")
    #     return True

    # def remove_stale_workers_by_expiration(self):
    #     expire = time.time() - CONTROLLER_HEART_BEAT_EXPIRATION
    #     to_delete = []
    #     for worker_name, w_info in self.worker_info.items():
    #         if w_info.check_heart_beat and w_info.last_heart_beat < expire:
    #             logger.info("time out, geting worker status")
    #             r = self.get_worker_status(worker_name)
    #             if r is None:
    #                 logger.info("model not exist")
    #                 to_delete.append(worker_name)
    #             else:
    #                 self.worker_info[worker_name].last_heart_beat = time.time()
    #                 rds.set(worker_info_key, serialize(self.worker_info))
    #                 logger.info(f"model exists , change last heart beat{worker_name}")
    #     for worker_name in to_delete:
    #         self.remove_worker(worker_name)

    # def handle_no_worker(self, params):
    #     logger.info(f"no worker: {params['model']}")
    #     ret = {
    #         "text": SERVER_ERROR_MSG,
    #         "error_code": ErrorCode.CONTROLLER_NO_WORKER,
    #     }
    #     return json.dumps(ret).encode() + b"\0"

    # def handle_worker_timeout(self, worker_address):
    #     logger.info(f"worker timeout: {worker_address}")
    #     ret = {
    #         "text": SERVER_ERROR_MSG,
    #         "error_code": ErrorCode.CONTROLLER_WORKER_TIMEOUT,
    #     }
    #     return json.dumps(ret).encode() + b"\0"

    # # Let the controller act as a worker to achieve hierarchical
    # # management. This can be used to connect isolated sub networks.
    # def worker_api_get_status(self):
    #     model_names = set()
    #     speed = 0
    #     queue_length = 0

    #     for w_name in self.worker_info:
    #         worker_status = self.get_worker_status(w_name)
    #         if worker_status is not None:
    #             model_names.update(worker_status["model_names"])
    #             speed += worker_status["speed"]
    #             queue_length += worker_status["queue_length"]

    #     model_names = sorted(list(model_names))
    #     return {
    #         "model_names": model_names,
    #         "speed": speed,
    #         "queue_length": queue_length,
    #     }

    # def worker_api_generate_stream(self, params):
    #     worker_addr = self.get_worker_address(params["model"])
    #     if not worker_addr:
    #         yield self.handle_no_worker(params)

    #     try:
    #         response = requests.post(
    #             worker_addr + "/worker_generate_stream",
    #             json=params,
    #             stream=True,
    #             timeout=WORKER_API_TIMEOUT,
    #         )
    #         for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
    #             if chunk:
    #                 yield chunk + b"\0"
    #     except requests.exceptions.RequestException as e:
    #         yield self.handle_worker_timeout(worker_addr)
    
    # def register_daemon(
    #     self, data: dict
    # ):
    #     # 若不添加进程间共享，则每个worker进程都会注册一次，需要解决
    #     daemon_id = data.get('daemon_id', data.get('daemon_IP'))
    #     flag = True
    #     if daemon_id not in self.daemon_info:
    #         logger.info(f"Register done: {data.get('daemon_name')}, {data.get('daemon_IP')}")
    #     else:
    #         logger.info("Daemon exists!")
    #         flag = False
    #     self.daemon_info[daemon_id] = DaemonInfo(**data)
    #     t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #     data['time'] = t
    #     mongo_db.daemon_info.insert_one(data)
    #     return flag
      
    # def list_daemons(self):
    #     invalid_daemons=[]
    #     for key, info in self.daemon_info.items():
    #         daemon_heartbeat=f"http://{info.daemon_IP}:{info.daemon_port}/heartbeat"
    #         try:
    #             requests.get(daemon_heartbeat,timeout=5)
    #         except Exception:
    #             invalid_daemons.append(key)
    #     for k in invalid_daemons:
    #         del self.daemon_info[k]
    #     return {key: d.to_dict() for key, d in self.daemon_info.items()}


class Deploy_Params(BaseModel):
    model_config_id: str
    cluster_id: str
    image_id: str
    name: str
    ip: str
    port: str = None
    node_id: str
    gpu_devices: str
    backend: str = "vllm"

@app.post("/model/deploy")
def deploy(deploy_params: Deploy_Params):
    model_config_id = deploy_params.model_config_id
    cluster_id = deploy_params.cluster_id
    image_id = deploy_params.image_id

    # 部署模型
    
    return {"status_code": 200, "msg": ""}

@app.post("/register_worker")
async def register_worker(request: Request):
    data = await request.json()
    controller.register_worker(
        data["worker_name"], data["check_heart_beat"], data.get("worker_status", None)
    )

controller = Controller()

# 通过代码启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run("cluster_controller:app", host="0.0.0.0", port=7911, reload=True)
