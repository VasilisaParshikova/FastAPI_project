from fastapi import FastAPI, Path
from database import engine, session
from models import Base

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()

@app.post("/api/tweets")
async def recipes():
    pass

@app.post("/api/medias")
async def recipes():
    pass

@app.delete("/api/tweets/{id}")
async def recipes():
    pass

@app.post("/api/tweets/{id}/likes")
async def recipes():
    pass


@app.delete("/api/tweets/{id}/likes")
async def recipes():
    pass

@app.post("/api/users/{id}/follow")
async def recipes():
    pass

@app.delete("/api/users/{id}/follow")
async def recipes():
    pass

@app.get("/api/tweets")
async def recipes():
    pass


@app.get("/api/users/me")
async def recipes():
    pass

@app.get("/api/users/{id}")
async def recipes():
    pass


