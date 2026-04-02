from contextlib import asynccontextmanager

from decouple import config
from fastapi import FastAPI
from fastapi.responses import Response
from playwright.async_api import async_playwright
from pydantic import BaseModel

from utils.constants import PDF_SETTINGS, WAIT_TIMEOUT


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.playwright = await async_playwright().start()
    app.state.browser = await app.state.playwright.chromium.launch(headless=True)
    yield
    await app.state.browser.close()
    await app.state.playwright.stop()


app = FastAPI(lifespan=lifespan)


class ReportData(BaseModel):
    id: int
    token: str


@app.get("/")
async def root():
    return


def get_prepare_to_request(report_id: int, token: str, source: str, subdomain: str = None):
    host = config("HOST", "localhost:4200")
    url = f"https://{subdomain}.{host}/u/reports/{report_id}/pdf"

    if not "direct" in host:
        url = f"http://{host}/u/reports/{report_id}/pdf"
    cookies = [dict(name=f"{source}.token", value=token, url=url)]
    return url, cookies


@app.get("/report-pdf/")
async def generate_pdf_for_report(report_id: int, token: str, source: str, subdomain: str = None):
    """
    Args:
        report_id: айди отчета
        token: токен юзера, который запустил фоновый (нужно для формирования куки)
        source: dev или prod (нужно для формирования куки)
        subdomain: домен компании (нужно для формирования куки)

    Returns:
        Response
    """
    headers = {"Content-Disposition": f"inline; filename=report_{report_id}.pdf"}
    url, cookies = get_prepare_to_request(
        report_id, token, source, subdomain
    )

    context = await app.state.browser.new_context()
    await context.add_cookies(cookies)
    page = await context.new_page()
    await page.goto(url)
    await page.wait_for_load_state("networkidle", timeout=WAIT_TIMEOUT)
    report_pdf = await page.pdf(**PDF_SETTINGS)
    await context.close()

    return Response(report_pdf, media_type="application/pdf", headers=headers)
