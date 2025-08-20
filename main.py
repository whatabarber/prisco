import os, json
from datetime import datetime, timedelta, timezone
from dateutil import parser
import requests
from config import DISCORD_WEBHOOK, DASHBOARD_JSON_URL, LOCAL_TZ, OUTPUT_DIR, LOOKAHEAD_DAYS, MAX_FAVORITE_ML
from bovada import fetch_bovada_events
from analysis import choose_pick
from utils import to_local, time_slot_label
from parlay import build_parlay
from github_deploy import deploy_to_vercel

os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_event(ev):
    return {
        "league": ev.get("league"),
        "home": ev.get("home"),
        "away": ev.get("away"),
        "kickoff_utc": ev.get("kickoff_utc"),
        "moneyline": ev.get("moneyline"),
        "spread": ev.get("spread"),
    }

def within_lookahead(ev_iso, days):
    if not ev_iso:
        return False
    dt = parser.parse(ev_iso)
    now = datetime.now(timezone.utc)
    return now <= dt <= now + timedelta(days=days)

def generate():
    events = fetch_bovada_events()
    candidates = [
        normalize_event(e)
        for e in events
        if e.get("league") in ("NFL", "CFB") and within_lookahead(e.get("kickoff_utc"), LOOKAHEAD_DAYS)
    ]

    results = []
    for ev in candidates:
        kickoff_utc = parser.parse(ev["kickoff_utc"]) if ev.get("kickoff_utc") else None
        kickoff_local = to_local(kickoff_utc, LOCAL_TZ) if kickoff_utc else None
        pick = choose_pick(ev, MAX_FAVORITE_ML)

        matchup = f"{ev['away']} at {ev['home']}"
        res = {
            "league": ev["league"],
            "week_label": "",
            "kickoff_local": kickoff_local.strftime("%Y-%m-%d %I:%M %p %Z") if kickoff_local else None,
            "slot": time_slot_label(kickoff_local) if kickoff_local else "",
            "matchup": matchup,
            "moneyline": ev["moneyline"],
            "spread": ev["spread"],
            "pick_type": pick["pick_type"],
            "pick": pick["pick_text"],
            "projected_score": pick["projected_score"],
            "reasoning": pick["reasoning"],
        }
        results.append(res)

    parlay_nfl = build_parlay(results, "NFL")
    parlay_cfb = build_parlay(results, "CFB")

    payload = {
        "generated_at": to_local(datetime.now(timezone.utc), LOCAL_TZ).isoformat(),
        "leagues": ["NFL", "CFB"],
        "games": results,
        "parlays": {"NFL": parlay_nfl, "CFB": parlay_cfb},
    }
    ts = to_local(datetime.now(timezone.utc), LOCAL_TZ).strftime("%Y%m%d_%H%M")
    out_path = os.path.join(OUTPUT_DIR, f"picks_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_path, payload

def to_discord(payload):
    if not DISCORD_WEBHOOK:
        print("No DISCORD_WEBHOOK set in config.py - skipping Discord send.")
        return

    embeds = []
    for g in payload["games"][:10]:
        desc = (
            f"Time: {g.get('slot','')} - {g.get('kickoff_local','')}\n"
            f"Pick: {g.get('pick','')}\n"
            f"Projected: {g.get('projected_score','')}\n"
            f"Why: {g.get('reasoning','')}"
        )
        embeds.append({"title": f"{g['league']} • {g['matchup']}", "description": desc})

    content = "Weekly Picks (Prisco-style)\n"
    if DASHBOARD_JSON_URL:
        content += f"Dashboard JSON: {DASHBOARD_JSON_URL}\n"

    for i in range(0, len(embeds), 10):
        chunk = {"content": content if i == 0 else None, "embeds": embeds[i:i+10]}
        try:
            requests.post(DISCORD_WEBHOOK, json=chunk, timeout=15)
        except Exception as e:
            print("Discord send error:", e)

    parlays = payload.get("parlays", {})
    for league, p in parlays.items():
        legs = "\n".join([f"- {leg}" for leg in p.get("legs", [])])
        msg = {"content": f"{league} 3-Leg Spread Parlay\n{legs}\nNote: {p.get('notes','')}"}
        try:
            requests.post(DISCORD_WEBHOOK, json=msg, timeout=15)
        except Exception as e:
            print("Discord send error:", e)

if __name__ == "__main__":
    path, payload = generate()
    print(f"JSON written to: {path}")
    to_discord(payload)
if __name__ == "__main__":
    path, payload = generate()
    print(f"JSON written to: {path}")
    
    # Send to Discord
    to_discord(payload)
    
    # Auto-deploy to Vercel
    print("\n🚀 Deploying to Vercel...")
    deploy_success = deploy_to_vercel(payload)
    
    if deploy_success:
        print("✅ All done! Check Discord and https://prisco.vercel.app/")
    else:
        print("⚠️  Discord sent, but Vercel deployment failed")