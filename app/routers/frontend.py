from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/ui", tags=["Frontend"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/ingredients", response_class=HTMLResponse, include_in_schema=False)
async def ingredients_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "ingredients"})


@router.get("/recipes", response_class=HTMLResponse, include_in_schema=False)
async def recipes_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "recipes"})
