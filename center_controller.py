from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# 定义一个数据模型用于接收 POST 请求的数据
class Item(BaseModel):
    name: str
    price: float
    description: str = None

# GET 请求示例
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# 动态路由的 GET 请求
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# POST 请求示例
@app.post("/items/")
def create_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}

# 通过代码启动 FastAPI 服务器
if __name__ == "__main__":
    uvicorn.run("center_controller:app", host="127.0.0.1", port=7910, reload=True)
