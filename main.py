from fastapi import FastAPI

from routers.pair import pair_router

app = FastAPI()

app.include_router(router=pair_router)


@app.get("/")
async def root():
    return {"Hello World": "It works!"}
