
from typing import List, Dict

def build_parlay(games: List[Dict], league: str, legs: int = 3) -> Dict:
    spread_candidates = []
    for g in games:
        if g.get("league") != league:
            continue
        if g.get("pick_type") == "spread" and g.get("pick"):
            price = None
            if "(" in g["pick"] and ")" in g["pick"]:
                try:
                    price = int(g["pick"].split("(")[-1].split(")")[0])
                except:
                    price = None
            line = None
            try:
                parts = g["pick"].split()
                line = float(parts[1])
            except:
                pass
            spread_candidates.append((g, abs(line) if line is not None else 99, abs(price) if price is not None else 999))

    spread_candidates.sort(key=lambda t: (t[1] not in (2.5,3.0,3.5,6.5,7.0,7.5), abs(t[2]-110)))
    legs_sel = [t[0] for t in spread_candidates[:legs]]

    return {
        "league": league,
        "legs": [g["pick"] for g in legs_sel],
        "notes": "Key numbers prioritized; balanced juice; matchup edges from writeups."
    }
