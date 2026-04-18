import os
from playwright.async_api import async_playwright

username = os.getenv("STEAM_USERNAME")
password = os.getenv("STEAM_PASSWORD")

async def login_all_sites_async():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        print("Start login buff")
        cookies = await login_buff(browser, username, password)

        print("Cookies collected:", len(cookies))
        await browser.close()


async def login_buff(browser, username: str, password: str):
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 Chrome/120",
    )

    page = await context.new_page()
    await page.goto("https://buff.163.com", wait_until="domcontentloaded")

    await page.wait_for_selector("text=Login/Register")
    await page.click("text=Login/Register")

    async with page.expect_popup() as popup_info:
        await page.click("text=Other login methods")

    popup = await popup_info.value

    login_section = popup.locator("div[data-featuretarget='login']")

    await login_section.locator("input[type='text']").fill(username)
    await login_section.locator("input[type='password']").fill(password)
    await login_section.locator("button", has_text="Sign in").click()

    cookies = await page.context.cookies()
    return cookies