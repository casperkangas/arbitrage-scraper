import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def extract_match_data(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Loading Veikkaus Pitkäveto...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector('[data-testid="subpage-game-row"]', timeout=15000)
        
        match_rows = page.locator('[data-testid="subpage-game-row"]')
        count = await match_rows.count()
        print(f"Found {count} total matches. Filtering for active 2-way Match Winner markets...\n")
        
        scraped_data = []
        
        for i in range(count):
            row = match_rows.nth(i)
            
            home_team = await row.locator('.gameinfo-teams-team--home').inner_text()
            away_team = await row.locator('.gameinfo-teams-team--away').inner_text()
            
            # Target buttons specifically by their testing IDs, bypassing all containers
            buttons = row.locator('button[data-testid$="-MONEY_LINE"], button[data-testid$="-MATCH_WINNER"]')
            button_count = await buttons.count()
            
            # Strict filter: Exactly 2 buttons guarantees a 2-way, non-suspended Lopputulos market
            if button_count != 2:
                continue
                
            odds = []
            for b in range(button_count):
                button = buttons.nth(b)
                odd_text = await button.inner_text()
                # Clean the string and convert to float
                clean_odd = float(odd_text.strip().replace(',', '.'))
                odds.append(clean_odd)
            
            scraped_data.append({
                "Home Team": home_team,
                "Away Team": away_team,
                "Veikkaus Odd 1": odds[0],
                "Veikkaus Odd 2": odds[1]
            })
            
        await browser.close()
        
        df = pd.DataFrame(scraped_data)
        
        if not df.empty:
            print(df.head(10))
            output_file = "veikkaus_odds.xlsx"
            df.to_excel(output_file, index=False)
            print(f"\nData successfully exported to {output_file}")
        else:
            print("No active 2-way Match Winner markets found.")

if __name__ == "__main__":
    target_url = "https://www.veikkaus.fi/fi/vedonlyonti/pitkaveto"
    asyncio.run(extract_match_data(target_url))