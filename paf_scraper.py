import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def extract_paf_geneva(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Loading PAF Sports Hub Tennis page...")
        await page.goto(url, wait_until="networkidle")
        
        # Step 1: Wait directly for the match list items to render
        await page.wait_for_selector('.KambiBC-sandwich-filter__event-list-item', timeout=15000)
        
        # Step 2: Grab all match rows immediately, ignoring sections
        match_rows = page.locator('.KambiBC-sandwich-filter__event-list-item')
        count = await match_rows.count()
        print(f"Found {count} total matches. Filtering strictly for 2-way Match Winner markets...\n")
        
        scraped_data = []
        
        # Step 3: Iterate through the match rows
        for i in range(count):
            row = match_rows.nth(i)
            
            team_names_locator = row.locator('.KambiBC-event-participants__name-participant-name')
            if await team_names_locator.count() != 2:
                continue
                
            home_team = await team_names_locator.nth(0).inner_text()
            away_team = await team_names_locator.nth(1).inner_text()
            
            # The outcomes-2 filter ensures we strictly capture Match Winner markets
            match_winner_container = row.locator('.KambiBC-bet-offer--onecrosstwo.KambiBC-bet-offer--outcomes-2').first
            if await match_winner_container.count() == 0:
                continue
            
            buttons = match_winner_container.locator('button.KambiBC-betty-outcome')
            if await buttons.count() < 2:
                continue
            
            odds = []
            for b in range(2):
                button = buttons.nth(b)
                button_aria = await button.get_attribute('aria-label')
                
                if not button_aria or " at " not in button_aria:
                    odds.append(None)
                    continue
                
                odd_str = button_aria.split(" at ")[-1].strip()
                
                if odd_str == "—" or odd_str == "-":
                    odds.append(None)
                else:
                    try:
                        clean_odd = float(odd_str.replace(',', '.'))
                        odds.append(clean_odd)
                    except ValueError:
                        odds.append(None)
            
            if None in odds:
                continue

            scraped_data.append({
                "Home Team": home_team.strip(),
                "Away Team": away_team.strip(),
                "PAF Odd 1": odds[0],
                "PAF Odd 2": odds[1]
            })
            
        await browser.close()
        
        df = pd.DataFrame(scraped_data)
        
        if not df.empty:
            print(df.head(10))
            output_file = "paf_geneva_odds.xlsx"
            df.to_excel(output_file, index=False)
            print(f"\nData successfully exported to {output_file}")
        else:
            print("No active ATP Geneva Match Winner markets found on PAF.")

if __name__ == "__main__":
    target_url = "https://www.paf.fi/en/vedonlyonti#/sports-hub/tennis"
    asyncio.run(extract_paf_geneva(target_url))