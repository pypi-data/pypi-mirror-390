import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def extract_data():
    email = os.getenv('TD_EMAIL')
    password = os.getenv('TD_PASSWORD')
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await (await browser.new_context()).new_page()
    
    # Login
    print("Logging in...")
    await page.goto("https://2.timedoctor.com/login", wait_until='load')
    await page.wait_for_timeout(2000)
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(5000)
    
    # Go to projects report
    print("Going to projects report...")
    await page.goto("https://2.timedoctor.com/projects-report", wait_until='load')
    await page.wait_for_timeout(3000)
    
    # Click "Expand All" button
    print("\nLooking for Expand All button...")
    expand_button = await page.query_selector('button:has-text("Expand All"), [aria-label*="Expand"]')
    if expand_button:
        print("Clicking Expand All...")
        await expand_button.click()
        await page.wait_for_timeout(2000)
    
    await page.screenshot(path='expanded_view.png')
    print("Screenshot: expanded_view.png")
    
    # Get all text content
    print("\nExtracting page content...")
    content = await page.content()
    
    # Look for time values in HH:MM:SS format
    import re
    time_values = re.findall(r'\d+h\s+\d+m|\d+:\d+:\d+', content)
    print(f"\nFound {len(time_values)} time values:")
    for val in time_values[:10]:
        print(f"  {val}")
    
    # Try to find project/task structure
    print("\nLooking for project/task elements...")
    
    # Look for project rows
    projects = await page.query_selector_all('[class*="project"], [role="row"]')
    print(f"Found {len(projects)} potential project/task rows")
    
    # Try specific selectors
    print("\nTrying to extract data...")
    
    # Get all visible text
    body = await page.query_selector('body')
    all_text = await body.inner_text()
    
    lines = all_text.split('\n')
    print("\nPage content (first 30 lines):")
    for i, line in enumerate(lines[:30]):
        if line.strip():
            print(f"  {i+1}: {line.strip()}")
    
    print("\nWaiting 30 seconds - explore the expanded view...")
    await asyncio.sleep(30)
    
    await browser.close()
    await playwright.stop()

asyncio.run(extract_data())
