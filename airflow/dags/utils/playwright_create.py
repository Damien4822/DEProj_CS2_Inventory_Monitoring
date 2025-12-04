from playwright.async_api import async_playwright

async def create_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    return playwright, browser, context, page