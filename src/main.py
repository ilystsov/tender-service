from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.routes.tenders import router as tenders_router

app = FastAPI()


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



@app.get("/api/ping", response_class=PlainTextResponse)
def ping():
    return "ok"
