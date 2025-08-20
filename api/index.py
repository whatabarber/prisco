from flask import Flask, render_template_string
import json

app = Flask(__name__)

# Current picks data (auto-updated by main.py)
PICKS_DATA = {
  "generated_at": "2025-08-19T23:56:31.320782-05:00",
  "leagues": [
    "NFL",
    "CFB"
  ],
  "games": [
    {
      "league": "CFB",
      "week_label": "",
      "kickoff_local": "2025-08-23 11:00 AM CDT",
      "slot": "Saturday Morning",
      "matchup": "Iowa State at Kansas State",
      "moneyline": {
        "Kansas State": -140,
        "Iowa State": 120
      },
      "spread": {
        "team": "Kansas State",
        "line": -3.0,
        "price": -110
      },
      "pick_type": "spread",
      "pick": "Kansas State -3 (-110)",
      "projected_score": "Kansas State 26-21",
      "reasoning": "Key-number leverage on the spread. Kansas State profile fits the trenches and QB edge. Line sits near a key number; value angle. Public may chase narratives; we're pricing the number."
    }
  ],
  "parlays": {
    "NFL": {
      "league": "NFL",
      "legs": [],
      "notes": "Key numbers prioritized; balanced juice; matchup edges from writeups."
    },
    "CFB": {
      "league": "CFB",
      "legs": [
        "Kansas State -3 (-110)"
      ],
      "notes": "Key numbers prioritized; balanced juice; matchup edges from writeups."
    }
  }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🏈 Prisco Picks</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; padding: 15px; background: #1a1a1a; color: white; 
            min-height: 100vh;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px; border-radius: 12px; margin-bottom: 25px; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .header h1 { margin: 0 0 10px 0; font-size: 28px; }
        .header p { margin: 0; opacity: 0.9; }
        .stats { 
            display: grid; grid-template-columns: repeat(3, 1fr); 
            gap: 15px; margin: 25px 0; 
        }
        .stat-card { 
            background: #2d2d2d; padding: 20px; border-radius: 12px; text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .stat-number { font-size: 28px; font-weight: bold; color: #4CAF50; margin-bottom: 5px; }
        .stat-label { font-size: 14px; color: #bbb; }
        .picks-container { display: flex; flex-direction: column; gap: 20px; }
        .pick-card { 
            background: #2d2d2d; border-radius: 12px; padding: 20px; 
            border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .league { 
            background: #4CAF50; color: white; padding: 6px 12px; 
            border-radius: 20px; font-size: 12px; font-weight: bold; 
            display: inline-block; margin-bottom: 15px;
        }
        .league.nfl { background: #FF5722; }
        .matchup { font-size: 20px; font-weight: bold; margin: 15px 0; }
        .pick { 
            background: #FF9800; color: white; padding: 12px; 
            border-radius: 8px; margin: 15px 0; font-weight: bold; 
            font-size: 16px;
        }
        .time-slot { color: #2196F3; font-weight: bold; margin: 10px 0; }
        .reasoning { color: #bbb; margin: 15px 0; font-style: italic; line-height: 1.4; }
        .parlay-section { 
            background: #2d2d2d; border-radius: 12px; padding: 25px; 
            margin: 25px 0; border-left: 4px solid #9C27B0; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .parlay-section h2 { margin-top: 0; color: #9C27B0; }
        .parlay-leg { 
            background: #9C27B0; color: white; padding: 10px 15px; 
            margin: 8px 0; border-radius: 8px; 
        }
        .no-games { 
            text-align: center; padding: 40px; color: #666; 
            background: #2d2d2d; border-radius: 12px;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .header { padding: 20px; }
            .header h1 { font-size: 24px; }
            .pick-card { padding: 15px; }
            .matchup { font-size: 18px; }
            .stats { gap: 10px; }
            .stat-card { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏈 Prisco-Style Picks</h1>
        <p>{{ generated_at }}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ total_games }}</div>
            <div class="stat-label">Total Games</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ nfl_games }}</div>
            <div class="stat-label">NFL Games</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ cfb_games }}</div>
            <div class="stat-label">CFB Games</div>
        </div>
    </div>

    <div class="picks-container">
        {% if games %}
            {% for game in games %}
            <div class="pick-card">
                <span class="league{% if game.league == 'NFL' %} nfl{% endif %}">{{ game.league }}</span>
                <div class="matchup">{{ game.matchup }}</div>
                <div class="time-slot">{{ game.slot }} - {{ game.kickoff_local }}</div>
                <div class="pick">{{ game.pick }}</div>
                <div><strong>Projected:</strong> {{ game.projected_score }}</div>
                <div class="reasoning">{{ game.reasoning }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-games">
                <h3>No games available</h3>
                <p>Picks will appear here when games are scheduled.</p>
            </div>
        {% endif %}
    </div>

    {% if parlays and (parlays.NFL.legs or parlays.CFB.legs) %}
    <div class="parlay-section">
        <h2>🎯 3-Leg Parlays</h2>
        {% for league, parlay in parlays.items() %}
            {% if parlay.legs %}
            <h3>{{ league }} Parlay</h3>
            {% for leg in parlay.legs %}
            <div class="parlay-leg">{{ leg }}</div>
            {% endfor %}
            {% endif %}
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

def index():
    """Main route for Vercel"""
    data = PICKS_DATA
    games = data.get('games', [])
    
    return render_template_string(HTML_TEMPLATE,
        generated_at=data.get('generated_at', 'No picks available'),
        games=games,
        parlays=data.get('parlays', {}) or {},
        total_games=len(games),
        nfl_games=len([g for g in games if g.get('league') == 'NFL']),
        cfb_games=len([g for g in games if g.get('league') == 'CFB'])
    )

# For Vercel serverless
app = index
