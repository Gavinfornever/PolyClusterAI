from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import requests
import json

app = FastAPI()

center_controller_address = "http://127.0.0.1:7910"

# class Apiserver():
#     ip = "127.0.0.1"
#     port = "7999"
#     center_controller_address = "http://127.0.0.1:7910"

#     def __init__(self) -> None:
#         pass

@app.get("/v1/dashboard")
def dashboard():
    response = requests.get(center_controller_address+"/cluster/dashboard")
    return response.json()

# 动态路由的 GET 请求
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     center_controller_address = "http://127.0.0.1"
#     response = requests.get("")
#     return {"item_id": item_id, "q": q}

class Deploy_Params(BaseModel):
    model_config_id: str
    cluster_id: str
    image_id: str
    name: str
    ip: str
    port: str = None
    node_id: str = None
    gpu_devices: str
    backend: str = "vllm"

@app.post("/v1/deploy")
def deploy(deploy_params: Deploy_Params):
    # 透传
    response = requests.post(center_controller_address+"/model/deploy", data=deploy_params.model_dump_json())
    return response.json()

# 通过代码启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run("apiserver:app", host="127.0.0.1", port=7999, reload=True)
