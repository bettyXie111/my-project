from fastapi import FastAPI

app = FastAPI(title="我的项目API", description="PRD 后端接口")

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}