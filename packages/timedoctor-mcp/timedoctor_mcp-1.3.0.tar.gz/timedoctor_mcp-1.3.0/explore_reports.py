"""
Interactive script to explore Time Doctor reports
and figure out the correct selectors
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()


async def explore_reports():
    """Interactively explore Time Doctor reports."""

    email = os.getenv('TD_EMAIL')
    password = os.getenv('TD_PASSWORD')

    print("═" * 70)
    print("Time Doctor Reports Explorer")
    print("═" * 70)
    print()
    print("This script will:")
    print("  1. Login to Time Doctor")
    print("  2. Navigate to Reports section")
    print("  3. Show you what's available")
    print("  4. Help identify the correct selectors")
    print()

    playwright = None
    browser = None

    try:
        playwright = await async_playwright().start()

        print("1️⃣  Launching browser (visible mode)...")
        browser = await playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        page.set_default_timeout(60000)

        # Login
        print("2️⃣  Logging in...")
        await page.goto("https://2.timedoctor.com/login", wait_until='load')
        await page.wait_for_timeout(2000)

        await page.fill('input[type="email"]', email)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"]')

        # Wait for dashboard
        await page.wait_for_timeout(5000)
        print(f"✅ Logged in! Current URL: {page.url}")
        print()

        # Navigate to Reports
        print("3️⃣  Navigating to Reports...")

        # Look for Reports link/button
        reports_selectors = [
            'a:has-text("REPORTS")',
            'a:has-text("Reports")',
            'button:has-text("REPORTS")',
            '[href*="report"]'
        ]

        reports_link = None
        for selector in reports_selectors:
            try:
                reports_link = await page.query_selector(selector)
                if reports_link:
                    print(f"   Found Reports link: {selector}")
                    await reports_link.click()
                    break
            except:
                continue

        if not reports_link:
            print("   ⚠️  Could not find Reports link in nav")
            print("   Let's try direct URL...")
            await page.goto("https://2.timedoctor.com/reports")

        await page.wait_for_timeout(3000)
        print(f"   Current URL: {page.url}")
        print()

        # Take screenshot
        await page.screenshot(path='reports_page.png')
        print("📸 Screenshot saved: reports_page.png")
        print()

        # Look for available report types
        print("4️⃣  Looking for available report types...")

        # Common report type selectors
        report_types = await page.query_selector_all('a[href*="report"], button:has-text("report")')

        if report_types:
            print(f"   Found {len(report_types)} report-related elements")
            for i, elem in enumerate(report_types[:10]):  # First 10
                try:
                    text = await elem.inner_text()
                    href = await elem.get_attribute('href')
                    if text or href:
                        print(f"   [{i+1}] Text: '{text}' | Href: {href}")
                except:
                    pass
        print()

        # Look for Projects & Tasks report
        print("5️⃣  Looking for 'Projects & Tasks' report...")

        project_task_selectors = [
            'a:has-text("Projects & Tasks")',
            'a:has-text("Projects and Tasks")',
            'a:has-text("Projects")',
            '[href*="project"]',
            'button:has-text("Projects")'
        ]

        for selector in project_task_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    print(f"   ✅ Found: {selector} - '{text}'")
            except:
                pass
        print()

        # Look for Timeline report
        print("6️⃣  Looking for 'Timeline' report...")

        timeline_selectors = [
            'a:has-text("Timeline")',
            '[href*="timeline"]',
            'button:has-text("Timeline")'
        ]

        timeline_elem = None
        for selector in timeline_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    print(f"   ✅ Found: {selector} - '{text}'")
                    timeline_elem = elem
                    break
            except:
                pass

        if timeline_elem:
            print()
            print("7️⃣  Clicking on Timeline report...")
            await timeline_elem.click()
            await page.wait_for_timeout(3000)

            print(f"   Current URL: {page.url}")
            await page.screenshot(path='timeline_report.png')
            print("   📸 Screenshot saved: timeline_report.png")
            print()

            # Look for data table/grid
            print("8️⃣  Looking for data on Timeline report...")

            # Look for table
            tables = await page.query_selector_all('table')
            print(f"   Found {len(tables)} tables")

            # Look for date picker
            date_inputs = await page.query_selector_all('input[type="date"], input[placeholder*="date"]')
            print(f"   Found {len(date_inputs)} date inputs")

            # Look for time data
            time_elements = await page.query_selector_all('[class*="time"], [class*="hour"], [class*="duration"]')
            print(f"   Found {len(time_elements)} time-related elements")

            # Get page content for analysis
            page_text = await page.content()

            # Look for common time patterns
            import re
            time_patterns = re.findall(r'\d+:\d+:\d+', page_text)
            if time_patterns:
                print(f"   Found {len(time_patterns)} time values (HH:MM:SS format)")
                print(f"   Examples: {time_patterns[:3]}")

            print()

        print("9️⃣  Interactive Mode")
        print("=" * 70)
        print()
        print("The browser will stay open for 60 seconds.")
        print("Please:")
        print("  • Navigate to different reports")
        print("  • Find where project/task time data is")
        print("  • Look at the URL patterns")
        print("  • Note any date selectors or filters")
        print()
        print("I'll wait while you explore...")
        print()

        for i in range(60, 0, -10):
            print(f"   ⏱️  {i} seconds remaining...")
            await asyncio.sleep(10)

        print()
        print("🔟 Taking final screenshot...")
        await page.screenshot(path='final_exploration.png')
        print("   📸 Screenshot saved: final_exploration.png")
        print(f"   Final URL: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print()
        print("Closing browser...")
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

    print()
    print("═" * 70)
    print("Exploration Complete!")
    print("═" * 70)
    print()
    print("Screenshots saved:")
    print("  • reports_page.png - Main reports page")
    print("  • timeline_report.png - Timeline report (if found)")
    print("  • final_exploration.png - Whatever you ended on")
    print()
    print("Next: Tell me what you found and I'll update the scraper!")


if __name__ == "__main__":
    asyncio.run(explore_reports())
