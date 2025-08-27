# static_html_deploy.py - Clean GitHub Pages deployment
import requests
import json
import base64
from datetime import datetime

# GitHub Configuration
GITHUB_USERNAME = "whatabarber"
GITHUB_REPO = "prisco"
GITHUB_TOKEN = "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"

def upload_static_html(payload):
    """Upload static HTML to GitHub Pages"""
    
    if not GITHUB_TOKEN:
        print("❌ Please add your GitHub token")
        return False
    
    # Generate HTML content
    games = payload.get('games', [])
    parlays = payload.get('parlays', {})
    
    # Generate stats
    total_games = len(games)
    nfl_games = len([g for g in games if g.get('league') == 'NFL'])
    cfb_games = len([g for g in games if g.get('league') == 'CFB'])
    
    # Generate game cards HTML
    game_cards = ""
    for game in games:
        league_class = "nfl" if game.get('league') == 'NFL' else "cfb"
        game_cards += f'''
        <div class="pick-card">
            <span class="league {league_class}">{game.get('league', '')}</span>
            <div class="matchup">{game.get('matchup', '')}</div>
            <div class="time-slot">{game.get('slot', '')} - {game.get('kickoff_local', '')}</div>
            <div class="pick">{game.get('pick', '')}</div>
            <div class="projected"><strong>Projected:</strong> {game.get('projected_score', '')}</div>
            <div class="reasoning">{game.get('reasoning', '')}</div>
        </div>
        '''
    
    # Generate parlay HTML
    parlay_html = ""
    if any(p.get('legs') for p in parlays.values()):
        parlay_html = '<div class="parlay-section"><h2>🎯 3-Leg Parlays</h2>'
        for league, parlay in parlays.items():
            if parlay.get('legs'):
                parlay_html += f'<h3>{league} Parlay</h3>'
                for leg in parlay['legs']:
                    parlay_html += f'<div class="parlay-leg">{leg}</div>'
        parlay_html += '</div>'
    
    # Complete HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏈 Prisco-Style Picks</title>
    <meta name="description" content="Pete Prisco-style NFL and CFB betting picks">
    <style>
        * {{ 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
            background: #0f0f0f; 
            color: #ffffff; 
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{ 
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header p {{ 
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 30px 0; 
        }}
        
        .stat-card {{ 
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{ 
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 8px;
        }}
        
        .stat-label {{ 
            color: #bbb;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .filter-tabs {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 30px 0;
        }}
        
        .filter-tab {{
            padding: 12px 24px;
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            color: #ccc;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }}
        
        .filter-tab:hover {{
            border-color: #666;
            background: #333;
        }}
        
        .filter-tab.active {{
            background: #4CAF50;
            border-color: #4CAF50;
            color: white;
        }}
        
        .filter-tab.nfl.active {{
            background: #FF5722;
            border-color: #FF5722;
        }}
        
        .filter-tab.cfb.active {{
            background: #4CAF50;
            border-color: #4CAF50;
        }}
        
        .filter-tab.parlay.active {{
            background: #9C27B0;
            border-color: #9C27B0;
        }}
        
        .picks-container {{ 
            display: grid;
            gap: 25px;
        }}
        
        .pick-card.hidden {{
            display: none;
        }}
        
        .parlay-section.hidden {{
            display: none;
        }}
        
        .pick-card {{ 
            background: #1a1a1a;
            border: 1px solid #333;
            border-left: 5px solid #4CAF50;
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
        }}
        
        .pick-card:hover {{
            border-left-color: #FF9800;
            transform: translateX(5px);
        }}
        
        .league {{ 
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .league.nfl {{ 
            background: #FF5722; 
        }}
        
        .matchup {{ 
            font-size: 1.4rem;
            font-weight: bold;
            margin: 15px 0;
            color: #fff;
        }}
        
        .time-slot {{ 
            color: #2196F3;
            font-weight: 600;
            margin: 10px 0;
            font-size: 0.9rem;
        }}
        
        .pick {{ 
            background: #FF9800;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: bold;
            font-size: 1.1rem;
            text-align: center;
        }}
        
        .projected {{
            margin: 15px 0;
            font-size: 1rem;
        }}
        
        .reasoning {{ 
            color: #ccc;
            margin: 15px 0;
            font-style: italic;
            line-height: 1.5;
            padding: 10px;
            background: #0a0a0a;
            border-radius: 8px;
        }}
        
        .parlay-section {{ 
            background: #1a1a1a;
            border: 1px solid #333;
            border-left: 5px solid #9C27B0;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
        }}
        
        .parlay-section h2 {{ 
            color: #9C27B0;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        
        .parlay-section h3 {{
            color: #fff;
            margin: 20px 0 15px 0;
            font-size: 1.3rem;
        }}
        
        .parlay-leg {{ 
            background: #9C27B0;
            color: white;
            padding: 12px 18px;
            margin: 8px 0;
            border-radius: 8px;
            font-weight: 500;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            color: #666;
            border-top: 1px solid #333;
        }}
        
        .no-games {{ 
            text-align: center;
            padding: 60px 20px;
            color: #666;
            background: #1a1a1a;
            border-radius: 12px;
            border: 1px solid #333;
        }}
        
        .no-games h3 {{
            margin-bottom: 15px;
            color: #999;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2rem; }}
            .pick-card {{ padding: 20px; }}
            .matchup {{ font-size: 1.2rem; }}
            .stats {{ gap: 15px; }}
            .stat-card {{ padding: 20px; }}
            .stat-number {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏈 Prisco-Style Picks</h1>
            <p>Last Updated: {payload.get('generated_at', 'Unknown')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_games}</div>
                <div class="stat-label">Total Games</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{nfl_games}</div>
                <div class="stat-label">NFL Games</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{cfb_games}</div>
                <div class="stat-label">CFB Games</div>
            </div>
        </div>

        <div class="filter-tabs">
            <div class="filter-tab active" onclick="filterGames('all')">All Games</div>
            <div class="filter-tab nfl" onclick="filterGames('nfl')">NFL</div>
            <div class="filter-tab cfb" onclick="filterGames('cfb')">CFB</div>
            <div class="filter-tab parlay" onclick="filterGames('parlays')">Parlays</div>
        </div>

        <div class="picks-container">
            {game_cards if games else '<div class="no-games"><h3>No Games Available</h3><p>Picks will appear here when games are scheduled.</p></div>'}
        </div>

        {parlay_html}

        <div class="footer">
            <p>Auto-generated by Prisco-Style Picks System</p>
            <p>Data from The Odds API • Updated automatically</p>
        </div>
    </div>

    <script>
        // Auto-refresh every 10 minutes
        setTimeout(() => {{
            location.reload();
        }}, 600000);
        
        // Filter games functionality
        function filterGames(category) {{
            const cards = document.querySelectorAll('.pick-card');
            const tabs = document.querySelectorAll('.filter-tab');
            const parlaySection = document.querySelector('.parlay-section');
            
            // Update active tab
            tabs.forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            if (category === 'parlays') {{
                // Hide all game cards, show only parlays
                cards.forEach(card => card.classList.add('hidden'));
                if (parlaySection) {{
                    parlaySection.classList.remove('hidden');
                }}
            }} else {{
                // Show/hide parlays section
                if (parlaySection) {{
                    parlaySection.classList.add('hidden');
                }}
                
                // Filter game cards
                cards.forEach(card => {{
                    const league = card.querySelector('.league');
                    if (!league) return;
                    
                    const leagueText = league.textContent.toLowerCase();
                    
                    if (category === 'all') {{
                        card.classList.remove('hidden');
                    }} else if (category === 'nfl' && leagueText === 'nfl') {{
                        card.classList.remove('hidden');
                    }} else if (category === 'cfb' && leagueText === 'cfb') {{
                        card.classList.remove('hidden');
                    }} else {{
                        card.classList.add('hidden');
                    }}
                }});
            }}
        }}
        
        // Add some interactive effects
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.pick-card');
            cards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(1.02)';
                    setTimeout(() => {{
                        this.style.transform = '';
                    }}, 200);
                }});
            }});
        }});
    </script>
</body>
</html>'''
    
    # Upload to GitHub
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file SHA if it exists
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()["sha"]
        else:
            sha = None
    except:
        sha = None
    
    # Upload HTML
    content_encoded = base64.b64encode(html_content.encode()).decode()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "message": f"Update picks HTML - {timestamp}",
        "content": content_encoded
    }
    
    if sha:
        data["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            print("✅ GitHub Pages deployment successful!")
            print(f"🔗 View at: https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}/")
            return True
        else:
            print(f"❌ GitHub upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ GitHub upload error: {e}")
        return False
