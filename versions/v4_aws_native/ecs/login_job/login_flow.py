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

    await page.goto("https://buff.163.com", wait_until="domcontentloaded", timeout=60000)

    await page.wait_for_selector("text=Login/Register", timeout=60000)
    await page.click("text=Login/Register")

    async with page.expect_popup() as popup_info:
        await page.wait_for_selector("text=Other login methods",timeout=60000)
        await page.click("text=Other login methods")

    popup = await popup_info.value

    login_section = popup.locator("div.page_content").locator("div[data-featuretarget='login']")
    username_input = login_section.locator("div", has_text="Sign in with account name").locator("input[type='text']")
    await username_input.is_visible(timeout=60000)
    password_input = login_section.locator("div", has_text="Password").locator("input[type='password']")
    await password_input.is_visible(timeout=60000)

    # Fill credentials
    await username_input.fill(username)
    await password_input.fill(password)
    await login_section.locator("button", has_text="Sign in").click()

    # Click the sign-in button to login buff
    final_login_form = popup.locator("form#openidForm")
    sign_in_button = final_login_form.locator("input[type='submit']", has_text="Sign In")

    # Wait for it to be visible and click
    await sign_in_button.wait_for(state="visible", timeout=60000)
    await sign_in_button.click()

    cookies = await page.context.cookies()
    target_domain = "buff.163.com"
    filtered_cookies = []

    for cookie in cookies:
        if target_domain in cookie["domain"] :
            filtered_cookies.append(cookie)
            
    return cookies