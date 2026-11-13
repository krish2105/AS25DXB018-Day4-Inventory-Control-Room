import sys, asyncio
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3100"
TABS = [("overview","Overview"),("abc","ABC Analysis"),("models","AI Models"),("safety","Safety Stock"),("simulator","Service-Level Simulator"),("compare","Before vs After AI")]
OUT = sys.argv[2] if len(sys.argv) > 2 else "screenshots"
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for scheme in ("light","dark"):
            ctx = await b.new_context(viewport={"width":1440,"height":900}, color_scheme=scheme, device_scale_factor=1)
            page = await ctx.new_page()
            msgs=[]
            page.on("console", lambda m: msgs.append(m.text) if m.type in ("error","warning") else None)
            for tid, label in TABS:
                if only and tid not in only: continue
                await page.goto(f"{BASE}/#{tid}", wait_until="networkidle")
                await page.wait_for_timeout(1200)
                await page.screenshot(path=f"{OUT}/web_{tid}_{scheme}.png", full_page=True)
            print(scheme, "console issues:", msgs[:5])
            await ctx.close()
        await b.close()
asyncio.run(main())
