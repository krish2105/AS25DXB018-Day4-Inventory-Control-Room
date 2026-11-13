import sys, asyncio
from playwright.async_api import async_playwright
BASE = "http://localhost:8601"
PAGES = [("overview",""),("abc_analysis","abc_analysis"),("ai_models","ai_models"),("safety_stock","safety_stock"),("simulator","simulator"),("before_after","before_after")]
OUT = sys.argv[1] if len(sys.argv)>1 else "screenshots"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for scheme in ("light","dark"):
            ctx = await b.new_context(viewport={"width":1440,"height":3300}, color_scheme=scheme)
            page = await ctx.new_page()
            for name, path in PAGES:
                await page.goto(f"{BASE}/{path}", wait_until="networkidle")
                await page.wait_for_timeout(3500)
                exc = await page.locator('[data-testid="stException"]').count()
                err = await page.locator('[data-testid="stAlert"]').count()
                print(scheme, name, "exceptions:", exc)
                if exc:
                    print((await page.locator('[data-testid="stException"]').first.inner_text())[:600])
                await page.screenshot(path=f"{OUT}/st_{name}_{scheme}.png", full_page=False)
            await ctx.close()
        await b.close()
asyncio.run(main())
