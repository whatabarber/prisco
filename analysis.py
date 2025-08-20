
from typing import Dict
from utils import implied_prob

def choose_pick(ev: Dict, max_fav_ml: int) -> Dict:
    moneyline = ev.get("moneyline") or {}
    spread = ev.get("spread")
    home = ev.get("home"); away = ev.get("away")

    fav, dog, fav_price, dog_price = None, None, None, None
    if moneyline:
        def find_price(team_name):
            if team_name in moneyline: return moneyline[team_name]
            for k,v in moneyline.items():
                if team_name and team_name.lower() in k.lower():
                    return v
            return None
        home_ml = find_price(home)
        away_ml = find_price(away)
        if home_ml is not None and away_ml is not None:
            if home_ml < away_ml:
                fav, fav_price = home, home_ml
                dog, dog_price = away, away_ml
            else:
                fav, fav_price = away, away_ml
                dog, dog_price = home, home_ml

    pick_type = None
    pick_text = None

    if spread and spread.get("team") and spread.get("price") is not None:
        s_team = spread["team"]; s_line = spread["line"]; s_price = spread["price"]
        if fav and s_team and fav.lower() in s_team.lower():
            pick_type = "spread"; pick_text = f"{fav} {s_line:+g} ({s_price})"
        else:
            if abs(s_line) in (2.5, 3.0, 3.5, 6.5, 7.0, 7.5):
                pick_type = "spread"; pick_text = f"{s_team} {s_line:+g} ({s_price})"

    if not pick_text and fav and fav_price is not None and fav_price >= max_fav_ml:
        pick_type = "moneyline"; pick_text = f"{fav} ML ({fav_price})"

    if not pick_text and dog and dog_price is not None:
        pick_type = "moneyline"; pick_text = f"{dog} ML ({dog_price})"

    proj = "24-20"
    if fav and fav_price is not None and dog_price is not None:
        p_fav = implied_prob(fav_price); p_dog = implied_prob(dog_price)
        gap = max(0.0, p_fav - p_dog)
        margin = int(round(4 + gap * 10))
        fav_pts = 24 + max(0, margin//2); dog_pts = 24 - max(0, margin//2) - (margin % 2)
        proj = f"{fav} {fav_pts}-{dog_pts}"

    reasoning = []
    if pick_type == "spread":
        reasoning.append("Key-number leverage on the spread.")
    else:
        reasoning.append("Moneyline aligns with matchup edge.")
    if fav:
        reasoning.append(f"{fav} profile fits the trenches and QB edge.")
    if spread:
        s_line = spread.get("line")
        if s_line is not None and abs(s_line) in (2.5, 3.0, 3.5, 6.5, 7.0, 7.5):
            reasoning.append("Line sits near a key number; value angle.")
    reasoning.append("Public may chase narratives; we're pricing the number.")

    return {
        "pick_type": pick_type or "lean",
        "pick_text": pick_text or (f"{fav} ML" if fav else "No bet"),
        "projected_score": proj,
        "reasoning": " ".join(reasoning)
    }
