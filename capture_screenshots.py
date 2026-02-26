import os
from playwright.sync_api import sync_playwright

def capture_mockups():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1000})

        # User Mockup
        user_path = os.path.abspath("user_mockup.html")
        page.goto(f"file://{user_path}")
        page.wait_for_timeout(1000) # Wait for Tailwind CDN
        page.screenshot(path="user_mockup.png", full_page=True)
        print(f"User mockup screenshot saved to user_mockup.png")

        # Admin Mockup
        admin_path = os.path.abspath("admin_mockup.html")
        page.goto(f"file://{admin_path}")
        page.wait_for_timeout(1000) # Wait for Tailwind CDN
        page.screenshot(path="admin_mockup.png", full_page=True)
        print(f"Admin mockup screenshot saved to admin_mockup.png")

        browser.close()

if __name__ == "__main__":
    capture_mockups()
