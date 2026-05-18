import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def extract_veikkaus_geneva(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Loading Veikkaus ATP Geneva page...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector('[data-testid="subpage-game-row"]', timeout=15000)
        
        match_rows = page.locator('[data-testid="subpage-game-row"]')
        count = await match_rows.count()
        print(f"Found {count} total matches. Filtering strictly for ATP Geneva...\n")
        
        scraped_data = []
        
        for i in range(count):
            row = match_rows.nth(i)
            
            # Extract and check the tournament description
            description_locator = row.locator('.teams-description span').first
            if await description_locator.count() > 0:
                description = await description_locator.inner_text()
                # Reject any match that is not part of ATP Geneva
                if "ATP Geneva" not in description:
                    continue
            else:
                continue
            
            home_team = await row.locator('.gameinfo-teams-team--home').inner_text()
            away_team = await row.locator('.gameinfo-teams-team--away').inner_text()
            
            # Extract only the Match Winner odds
            buttons = row.locator('button[data-testid$="-MATCH_WINNER"]')
            if await buttons.count() != 2:
                continue
                
            odds = []
            for b in range(2):
                button = buttons.nth(b)
                odd_text = await button.inner_text()
                # Standardize the decimal format
                clean_odd = float(odd_text.strip().replace(',', '.'))
                odds.append(clean_odd)
            
            scraped_data.append({
                "Home Team": home_team.strip(),
                "Away Team": away_team.strip(),
                "Veikkaus Odd 1": odds[0],
                "Veikkaus Odd 2": odds[1]
            })
            
        await browser.close()
        
        df = pd.DataFrame(scraped_data)
        
        if not df.empty:
            print(df.head(10))
            output_file = "veikkaus_geneva_odds.xlsx"
            df.to_excel(output_file, index=False)
            print(f"\nData successfully exported to {output_file}")
        else:
            print("No active ATP Geneva matches found.")

if __name__ == "__main__":
    target_url = "https://www.veikkaus.fi/fi/vedonlyonti/pitkaveto?t=77-70"
    asyncio.run(extract_veikkaus_geneva(target_url))