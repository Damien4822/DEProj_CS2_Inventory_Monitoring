from datetime import datetime,timedelta
from airflow import DAG
from airflow.decorators import task
from playwright.async_api import async_playwright
import asyncio
import json
from pathlib import Path

username=''
password=''
COOKIES_DIR = Path("/airflow/data/cookies")
default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
async def login_buff(browser, username:str, password:str):
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("http://buff.163.com")
    await page.click("text=Login/Register")

    async with page.expect_popup() as popup_info:
        await page.click("text=Other login methods")
        await page.wait_for_timeout(10000)

    popup = await popup_info.value
    await popup.fill("input[type='text']", username)
    await popup.fill("input[type='password']", password)
    await popup.wait_for_timeout(10000)

    await popup.wait_for_selector("button:has-text('Sign In')")
    await popup.click("button:has-text('Sign In')")
    await popup.wait_for_timeout(10000)

    await popup.locator('input[value="Sign In"]').click()

    cookies = await page.context.cookies()
    target_domain = "buff.163.com"
    filtered_cookies = []

    for cookie in cookies:
        if target_domain in cookie["domain"] :
            filtered_cookies.append(cookie)
    #for future scaling, consider using redis.
    return filtered_cookies
def save_cookies(site: str, cookies: list):
    path = COOKIES_DIR / f"{site}.json"
    with path.open("w") as f:
        json.dump(cookies, f, indent=2)
@task
def login_all_sites():
    async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage"],
            )
        try:
            buff_cookies = await login_buff(browser,username,password)
            save_cookies("buff",buff_cookies)
        finally:
            await browser.close()

    asyncio.run(run())


with DAG(
    'login_sites',
    default_args=default_args,
    description='Automation for login and get sites\'s cookies ',
    schedule='0 */6 * * *',#setup to run every 6hours 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['login', 'playwright'],
) as dag:
    
    login_all_sites()