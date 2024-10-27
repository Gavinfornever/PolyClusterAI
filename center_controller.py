from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

# 定义一个数据模型用于接收 POST 请求的数据
class Item(BaseModel):
    name: str
    price: float
    description: str = None

@app.get("/cluster/dashboard")
def dashboard():
    res = {
            "msg": "", 
            "result": {
                "num_model": 10,
                "num_instance": 20,
                "num_cluster": 2,
                "num_model_config": {},
                "gpu_utilization": 0.9,
                "cpu_utilization": 0.9,
            }
        }
    return res
    # return response.text

# 动态路由的 GET 请求
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# POST 请求示例
@app.post("/items/")
def create_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}

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

mock_model_config = {
    "_id":'model_xxx',
    "model_name":"llama3.1",
    "model_init_config":{},
    "deploy_config":{},
    "creator_id":"creator_www",
    "deployed":True
}

mock_cluster_config = {
    "_id":"cluster_yyy",
    "cluster_name":"muxi",
    "controller_url":"http://127.0.0.1:7911"
}

mock_image_config = {
    "_id":"image_mmm",
    "name":"vllm_0.5.0_post1",
    "cluster_id":"cluster_yyy",
}

@app.post("/model/deploy")
def deploy(deploy_params: Deploy_Params):
    model_config_id = deploy_params.model_config_id
    cluster_id = deploy_params.cluster_id
    image_id = deploy_params.image_id
    # 根据id拿到模型配置
    model_config = mock_model_config
    # 根据id拿到集群
    cluster_config = mock_cluster_config
    # 根据id拿到镜像配置
    image_config = mock_image_config
    # 给对应集群发送部署命令
    response = 
    # 发送其他信息
    return {"status_code": 200, "msg": ""}

# 通过代码启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run("center_controller:app", host="127.0.0.1", port=7910, reload=True)
