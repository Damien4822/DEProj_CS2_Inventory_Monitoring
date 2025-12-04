from playwright.async_api import async_playwright
import json
BUFF_STATE_FILE = "buff_state.json"


async def buff_login(username:str,password:str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False opens a visible window
        context = await browser.new_context()

        page = await browser.new_page()
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
        print(cookies)
        for cookie in cookies:
            if cookie["domain"] == target_domain:
                filtered_cookies.append(cookie)
        await page.wait_for_timeout(10000)
        await browser.close()

        return filtered_cookies