import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from playwright.sync_api import sync_playwright

app = FastAPI()

# 1. Define your secret key and the header name
API_KEY = "Ayman_Secret_2026"  # Change this to something very complex
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# 2. This function checks if the key is correct
async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return header_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


def get_policy_from_portal(citizen_id: str):
    # ... (Keep your same Playwright logic here) ...
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        page = browser.new_page()
        try:
            page.goto("https://portal1-0jeg.onrender.com/", timeout=60000)
            page.get_by_role("textbox", name="Username:").fill("admin")
            page.get_by_role("textbox", name="Password:").fill("admin123")
            page.get_by_role("button", name="Login").click()

            page.get_by_role("textbox", name="Citizen ID:").fill(citizen_id)
            page.get_by_role("button", name="Search").click()

            page.wait_for_selector("p:has-text('Policy Number:')", timeout=5000)
            result_text = page.locator("p:has-text('Policy Number:')").inner_text()
            return result_text.split("Policy Number: ")[1].strip()
        except:
            return None
        finally:
            browser.close()


# 3. Add 'Depends(get_api_key)' to protect this route
@app.get("/fetch-policy/{cid}")
def fetch_policy(cid: str, auth: str = Depends(get_api_key)):
    policy = get_policy_from_portal(cid)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"status": "success", "policy_number": policy}