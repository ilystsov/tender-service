from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.db.database import engine, BaseModel
from src.routes.tenders import router as tenders_router
from src.routes.bids import router as bids_router


app = FastAPI()


@app.on_event("startup")
def startup_event():
    print("Creating all tables in the database if they do not exist...")
    BaseModel.metadata.create_all(bind=engine)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"reason": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"reason": exc.errors()}
    )

app.include_router(tenders_router)
app.include_router(bids_router)

@app.get("/api/ping", response_class=PlainTextResponse)
def ping():
    return "ok"
