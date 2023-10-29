import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database.connect import get_db
from src.routes import contacts, auth, users

app = FastAPI()

origins = [
    "http://localhost:3000", "http://127.0.0.1:5500"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function is a middleware function that adds an X-Process-Time header to the response.
    The value of this header is the number of seconds it took to process the request.

    :param request: Request: Access the request object
    :param call_next: Call the next function in the middleware chain
    :return: A response object,
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing external APIs.

    :return: A fastapi limiter instance
    :doc-author: Trelent
    """
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    The read_root function is a view function that returns a dictionary
    containing the message &quot;REST APP CONTACTS v.10&quot;. The read_root function
    is mapped to the root URL of our application, which is /api/v.10/. When we
    access this URL in our browser, we will see the message returned by this
    view function.

    :return: A dictionary, which is converted to json and sent back to the client
    :doc-author: Trelent
    """
    return {"message": "REST APP CONTACTS v1.0"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If it doesn't, then we know there's an issue with our connection.

    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True)
