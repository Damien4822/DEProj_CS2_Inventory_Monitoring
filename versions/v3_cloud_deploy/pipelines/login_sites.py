from datetime import datetime,timedelta
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.utils.log.logging_mixin import LoggingMixin
import os

logger = LoggingMixin().log
username = os.getenv("STEAM_USERNAME")
password = os.getenv("STEAM_PASSWORD")
default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    "pool": "default_pool",
    'retry_delay': timedelta(minutes=5),
}
async def login_all_sites_async():
    from playwright.async_api import async_playwright
    from pyvirtualdisplay import Display
    from versions.v3_cloud_deploy.storage.redis_client import save_cookies
    
    display = Display(visible=1, size=(1920, 1080),backend="xvfb")
    display.start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],)
        
        logger.info("Start logging-in buff")
        buff_cookies = await login_buff(browser,username,password)
        logger.info("Saving buff's cookies")
        save_cookies("buff",buff_cookies)
        await browser.close()
        display.stop()

async def login_buff(browser, username:str, password:str):
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
    page = await context.new_page()
    await page.goto("https://buff.163.com",wait_until="domcontentloaded", timeout=60000)

    # Wait for login button or perform manual login
    await page.wait_for_selector("text=Login/Register", timeout=60000)
    await page.click("text=Login/Register")
    # Prepare to catch the popup (Steam login)
    async with page.expect_popup() as popup_info:
        await page.wait_for_selector("text=Other login methods",timeout=60000)
        await page.click("text=Other login methods")
        
    #inputing account's info ( im using an freshly created account, without steam guard and such)
    popup = await popup_info.value

    login_section = popup.locator("div.page_content").locator("div[data-featuretarget='login']")
    username_input = login_section.locator("div", has_text="Sign in with account name").locator("input[type='text']")
    await username_input.is_visible(timeout=30000)
    password_input = login_section.locator("div", has_text="Password").locator("input[type='password']")
    await password_input.is_visible(timeout=30000)

    # Fill credentials
    await username_input.fill(username)
    await password_input.fill(password)
    await login_section.locator("button", has_text="Sign in").click()

    # Click the sign-in button to login buff
    final_login_form = popup.locator("form#openidForm")
    final_login_form.wait_for(state="visible", timeout=30000)
    sign_in_button = final_login_form.locator("input[type='submit']", has_text="Sign In")

    # Wait for it to be visible and click
    await sign_in_button.wait_for(state="visible", timeout=30000)
    await sign_in_button.click()

    cookies = await page.context.cookies()
    target_domain = "buff.163.com"
    filtered_cookies = []

    for cookie in cookies:
        if target_domain in cookie["domain"] :
            filtered_cookies.append(cookie)
            
    return filtered_cookies

@task
def login_all_sites():
    import asyncio

    asyncio.run(login_all_sites_async())


with DAG(
    'login_sites_v2',
    default_args=default_args,
    description='Automation for login and get sites\'s cookies ',
    schedule='0 */6 * * *',#setup to run every 6hours 
    max_active_runs=1,
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['login', 'playwright','v2'],
) as dag:
    
    login_all_sites()