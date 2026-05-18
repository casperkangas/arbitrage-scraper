import pandas as pd
import difflib

def calculate_ap(odd1: float, odd2: float) -> float:
    if pd.isna(odd1) or pd.isna(odd2) or odd1 == 0 or odd2 == 0:
        return float('inf')
    return (1 / odd1) + (1 / odd2)

def generate_arbitrage_report():
    print("Loading odds data...")
    try:
        df_veikkaus = pd.read_excel('veikkaus_geneva_odds.xlsx')
        df_paf = pd.read_excel('paf_geneva_odds.xlsx')
    except FileNotFoundError as e:
        print(f"Error: Could not find the Excel files. {e}")
        return

    results = []
    
    veikkaus_home_teams = df_veikkaus['Home Team'].tolist()

    for index, paf_row in df_paf.iterrows():
        paf_home = paf_row['Home Team']
        paf_away = paf_row['Away Team']
        paf_odd1 = paf_row['PAF Odd 1']
        paf_odd2 = paf_row['PAF Odd 2']

        best_match = difflib.get_close_matches(paf_home, veikkaus_home_teams, n=1, cutoff=0.6)

        if best_match:
            veikkaus_match_home = best_match[0]
            veikkaus_row = df_veikkaus[df_veikkaus['Home Team'] == veikkaus_match_home].iloc[0]

            veikkaus_away = veikkaus_row['Away Team']
            veikkaus_odd1 = veikkaus_row['Veikkaus Odd 1']
            veikkaus_odd2 = veikkaus_row['Veikkaus Odd 2']

            # Calculate only the two valid cross-bookmaker betting scenarios
            scenarios = [
                ("Veikkaus Home / PAF Away", calculate_ap(veikkaus_odd1, paf_odd2), veikkaus_odd1, paf_odd2),
                ("PAF Home / Veikkaus Away", calculate_ap(paf_odd1, veikkaus_odd2), paf_odd1, veikkaus_odd2)
            ]

            scenarios.sort(key=lambda x: x[1])
            best_scenario = scenarios[0]
            best_strategy = best_scenario[0]
            best_ap = best_scenario[1]
            odd_1_val = best_scenario[2]
            odd_2_val = best_scenario[3]

            if best_ap < 1.0:
                profit_margin = f"{round((1 / best_ap - 1) * 100, 2)}%"
            else:
                profit_margin = "No Arbitrage"

            results.append({
                "Match": f"{paf_home} vs {paf_away}",
                "Best Strategy": best_strategy,
                "Odd 1": odd_1_val,
                "Odd 2": odd_2_val,
                "AP": round(best_ap, 4),
                "Profit Margin": profit_margin
            })

    results_df = pd.DataFrame(results)
    
    if not results_df.empty:
        results_df = results_df.sort_values(by="AP", ascending=True)
        
        print("\n--- Top Arbitrage Opportunities ---")
        print(results_df.head(5).to_string(index=False))
        
        output_file = "arbitrage_final_report.xlsx"
        results_df.to_excel(output_file, index=False)
        print(f"\nFinal report saved to {output_file}")
    else:
        print("No matches could be paired between the two datasets.")

if __name__ == "__main__":
    generate_arbitrage_report()