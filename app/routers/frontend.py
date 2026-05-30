from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/ui", tags=["Frontend"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/ingredients", response_class=HTMLResponse, include_in_schema=False)
async def ingredients_page(request: Request):
    return templates.TemplateResponse("ingredients.html", {"request": request})


@router.get("/recipes", response_class=HTMLResponse, include_in_schema=False)
async def recipes_page(request: Request):
    return templates.TemplateResponse("recipes.html", {"request": request})
