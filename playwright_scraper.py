import asyncio
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
        
        # Wait specifically for the game rows to appear in the DOM
        await page.wait_for_selector('[data-testid="subpage-game-row"]', timeout=15000)
        
        # Locate all match containers on the page
        match_rows = page.locator('[data-testid="subpage-game-row"]')
        count = await match_rows.count()
        print(f"Found {count} matches on the page.\n")
        
        # Loop through the first 5 matches for testing
        for i in range(min(5, count)):
            row = match_rows.nth(i)
            
            # Extract Team Names using the specific classes
            home_team = await row.locator('.gameinfo-teams-team--home').inner_text()
            away_team = await row.locator('.gameinfo-teams-team--away').inner_text()
            
            # Extract Odds. We target the generic 'bet-selection-button' and grab all of them in the row
            buttons = row.locator('.bet-selection-button')
            button_count = await buttons.count()
            
            odds = []
            for b in range(button_count):
                button = buttons.nth(b)
                # Check if the class list contains the placeholder class (meaning the odd is suspended)
                class_attribute = await button.get_attribute('class')
                
                if 'bet-selection-button-placeholder' in class_attribute:
                    odds.append("Suspended/Closed")
                else:
                    # Extract the text inside the span (e.g., "25,50") and clean it
                    odd_text = await button.inner_text()
                    odds.append(odd_text.strip())
            
            print(f"Match: {home_team} vs {away_team}")
            print(f"Odds Extracted: {odds}")
            print("-" * 40)
            
        await browser.close()

if __name__ == "__main__":
    target_url = "https://www.veikkaus.fi/fi/vedonlyonti/pitkaveto"
    asyncio.run(extract_match_data(target_url))