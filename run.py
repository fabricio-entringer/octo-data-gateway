import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:api", 
                host="0.0.0.0", 
                port=8000, 
                access_log=True,
                log_level="info")