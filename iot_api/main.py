from fastapi import FastAPI
from routers import account, data, module
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="iot_api")

origins = [
    "http://localhost",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(module.router)
app.include_router(data.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
