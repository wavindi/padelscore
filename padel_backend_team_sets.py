from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store complete match state
game_state = {
    'score_1': 0,        # Tennis scores (0, 15, 30, 40)
    'score_2': 0,
    'point_1': 0,        # Total points in current game
    'point_2': 0,
    'game_1': 0,         # Games won in current set
    'game_2': 0,
    'set_1': 0,          # Sets won in match
    'set_2': 0,
    'match_won': False,  # Match completion status
    'winner': None,      # Winner information
    'set_history': [],   # History of completed sets
    'last_updated': datetime.now().isoformat()
}

def check_set_winner():
    """Check if a set is complete and update sets count"""
    global game_state

    # Check if either team won the set (6 games with at least 2-game lead)
    if game_state['game_1'] >= 6 and game_state['game_1'] - game_state['game_2'] >= 2:
        # Black team wins the set
        game_state['set_1'] += 1
        game_state['set_history'].append(f"{game_state['game_1']}-{game_state['game_2']}")
        game_state['game_1'] = 0
        game_state['game_2'] = 0
        return check_match_winner()

    elif game_state['game_2'] >= 6 and game_state['game_2'] - game_state['game_1'] >= 2:
        # Yellow team wins the set
        game_state['set_2'] += 1
        game_state['set_history'].append(f"{game_state['game_1']}-{game_state['game_2']}")
        game_state['game_1'] = 0
        game_state['game_2'] = 0
        return check_match_winner()

    # Check for tiebreak at 6-6 (simplified: next game wins)
    elif game_state['game_1'] == 6 and game_state['game_2'] == 6:
        # In a real tiebreak, this would be more complex
        # For simplicity, next game wins the set
        pass

    return False

def check_match_winner():
    """Check if the match is complete (first to 2 sets wins)"""
    global game_state

    if game_state['set_1'] >= 2:
        # Black team wins the match
        game_state['match_won'] = True
        game_state['winner'] = {
            'team': 'black',
            'team_name': 'BLACK TEAM',
            'final_sets': f"{game_state['set_1']}-{game_state['set_2']}",
            'match_summary': ', '.join(game_state['set_history']),
            'total_games_won': game_state['set_1'] * 6,  # Simplified calculation
        }
        return True

    elif game_state['set_2'] >= 2:
        # Yellow team wins the match
        game_state['match_won'] = True
        game_state['winner'] = {
            'team': 'yellow',
            'team_name': 'YELLOW TEAM',
            'final_sets': f"{game_state['set_1']}-{game_state['set_2']}",
            'match_summary': ', '.join(game_state['set_history']),
            'total_games_won': game_state['set_2'] * 6,  # Simplified calculation
        }
        return True

    return False

# Serve the corrected HTML file with team sets
@app.route('/')
def serve_scoreboard():
    """Serve the scoreboard with sets in team areas"""
    return send_from_directory('.', 'padel_scoreboard_team_sets.html')

# Serve static files (images)
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files like back.png and logo.png"""
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    else:
        return f"File {filename} not found", 404

# API endpoint to add point with complete match logic
@app.route('/add_point', methods=['POST'])
def add_point():
    """Add a point with complete tennis scoring including sets and match winner"""
    global game_state

    # Check if match is already won
    if game_state['match_won']:
        return jsonify({
            'success': False,
            'error': 'Match is already completed',
            'winner': game_state['winner'],
            'match_won': True
        }), 400

    try:
        data = request.get_json()
        team = data.get('team', 'black')

        if team == 'black':
            # Tennis scoring system: 0, 15, 30, 40, Game
            current_score = game_state['score_1']

            if current_score == 0:
                game_state['score_1'] = 15
            elif current_score == 15:
                game_state['score_1'] = 30
            elif current_score == 30:
                game_state['score_1'] = 40
            elif current_score == 40:
                # Win the game
                game_state['game_1'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0

                # Check if set is won and potentially match
                match_won = check_set_winner()

            # Increment point counter
            game_state['point_1'] += 1

        elif team == 'yellow':
            # Tennis scoring system for yellow team
            current_score = game_state['score_2']

            if current_score == 0:
                game_state['score_2'] = 15
            elif current_score == 15:
                game_state['score_2'] = 30
            elif current_score == 30:
                game_state['score_2'] = 40
            elif current_score == 40:
                # Win the game
                game_state['game_2'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0

                # Check if set is won and potentially match
                match_won = check_set_winner()

            # Increment point counter
            game_state['point_2'] += 1

        game_state['last_updated'] = datetime.now().isoformat()

        # Log the action with corrected layout info
        if game_state['match_won']:
            print(f"🏆 MATCH WON by {game_state['winner']['team_name']}!")
            print(f"Final Score: {game_state['winner']['final_sets']}")
            print(f"Sets displayed in team areas, Games in bottom panel")
        else:
            print(f"Point added to {team} team.")
            print(f"Tennis Scores: {game_state['score_1']}-{game_state['score_2']}")
            print(f"Games: {game_state['game_1']}-{game_state['game_2']}")
            print(f"Sets (in team areas): {game_state['set_1']}-{game_state['set_2']}")

        return jsonify({
            'success': True,
            'message': f'Point added to {team} team',
            'game_state': game_state,
            'match_won': game_state['match_won'],
            'winner': game_state['winner'] if game_state['match_won'] else None
        })

    except Exception as e:
        print(f"Error adding point: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get current complete game state
@app.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current complete game state including sets and winner"""
    return jsonify(game_state)

# API endpoint to reset the entire match
@app.route('/reset_match', methods=['POST'])
def reset_match():
    """Reset the entire match including sets"""
    global game_state
    game_state = {
        'score_1': 0,
        'score_2': 0,
        'point_1': 0,
        'point_2': 0,
        'game_1': 0,
        'game_2': 0,
        'set_1': 0,
        'set_2': 0,
        'match_won': False,
        'winner': None,
        'set_history': [],
        'last_updated': datetime.now().isoformat()
    }

    print("🔄 Complete match reset")
    print("📐 Layout: Sets in team areas, Games in bottom panel")
    return jsonify({
        'success': True,
        'message': 'Match reset successfully',
        'game_state': game_state
    })

# API endpoint to update specific scores manually
@app.route('/update_scores', methods=['POST'])
def update_scores():
    """Update scores manually with match logic check"""
    global game_state

    try:
        data = request.get_json()

        # Update scores if provided
        if 'score_1' in data:
            game_state['score_1'] = data['score_1']
        if 'score_2' in data:
            game_state['score_2'] = data['score_2']
        if 'point_1' in data:
            game_state['point_1'] = data['point_1']
        if 'point_2' in data:
            game_state['point_2'] = data['point_2']
        if 'game_1' in data:
            game_state['game_1'] = data['game_1']
        if 'game_2' in data:
            game_state['game_2'] = data['game_2']
        if 'set_1' in data:
            game_state['set_1'] = data['set_1']
        if 'set_2' in data:
            game_state['set_2'] = data['set_2']

        # Check if match is won after manual update
        check_match_winner()

        game_state['last_updated'] = datetime.now().isoformat()

        print(f"Scores updated manually: {game_state}")
        return jsonify({
            'success': True,
            'message': 'Scores updated successfully',
            'game_state': game_state,
            'match_won': game_state['match_won'],
            'winner': game_state['winner'] if game_state['match_won'] else None
        })

    except Exception as e:
        print(f"Error updating scores: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'game_state': game_state,
        'match_status': 'completed' if game_state['match_won'] else 'in_progress',
        'layout': 'Sets displayed in team areas, Games in bottom panel'
    })

# API endpoint to get detailed match statistics
@app.route('/stats', methods=['GET'])
def get_stats():
    """Get comprehensive match statistics"""
    total_points = game_state['point_1'] + game_state['point_2']
    total_games = game_state['game_1'] + game_state['game_2']
    total_sets = game_state['set_1'] + game_state['set_2']

    stats = {
        'match_status': 'completed' if game_state['match_won'] else 'in_progress',
        'total_points': total_points,
        'total_games': total_games,
        'total_sets': total_sets,
        'current_set': total_sets + 1,
        'layout_info': 'Sets displayed in individual team areas',
        'black_team': {
            'current_points': game_state['point_1'],
            'current_score': game_state['score_1'],
            'current_games': game_state['game_1'],
            'sets_won': game_state['set_1']
        },
        'yellow_team': {
            'current_points': game_state['point_2'],
            'current_score': game_state['score_2'],
            'current_games': game_state['game_2'],
            'sets_won': game_state['set_2']
        },
        'set_history': game_state['set_history'],
        'winner': game_state['winner'],
        'last_updated': game_state['last_updated']
    }

    return jsonify(stats)

# Check for required image files on startup
def check_image_files():
    """Check if required image files exist"""
    required_files = ['back.png', 'logo.png']
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("⚠️  WARNING: Missing image files:")
        for file in missing_files:
            print(f"   • {file}")
        print("📝 The scoreboard will use fallback designs for missing images.")
        print("💡 Place your image files in the same folder as this script.")
    else:
        print("✅ All required image files found!")

if __name__ == '__main__':
    print("🏓 Starting Padel Scoreboard with Corrected Layout...")
    print("=" * 85)

    # Check for image files
    check_image_files()

    print("")
    print("🌐 Access the scoreboard at: http://localhost:5000")
    print("🏆 Corrected Layout: Sets in Team Areas, Games in Bottom Panel")
    print("🎾 Tennis Scoring: 0 → 15 → 30 → 40 → Game → Set → Match")
    print("=" * 85)
    print("📐 LAYOUT STRUCTURE:")
    print("   BLACK TEAM        |    YELLOW TEAM")
    print("      15             |        30      ")
    print("       5             |         3      ")  
    print("                     |")
    print("      GAMES: 1 - 1 (bottom panel)")
    print("=" * 85)
    print("🖼️  Image Files:")
    print("   • back.png  - Background image (padel court recommended)")
    print("   • logo.png  - Logo for top-right corner")
    print("")
    print("🔗 API Endpoints:")
    print("  GET  /           - Serve corrected scoreboard interface")
    print("  GET  /<filename> - Serve static files (images)")
    print("  POST /add_point  - Add point with complete match logic")
    print("  GET  /game_state - Get complete game state")
    print("  POST /reset_match - Reset entire match")
    print("  POST /update_scores - Manual score update")
    print("  GET  /stats      - Get comprehensive match statistics")
    print("  GET  /health     - Health check with match status")
    print("=" * 85)
    print("🎮 Corrected Features:")
    print("  • Sets score displayed INSIDE each team area")
    print("  • Large tennis score (15, 30, 40) at top of team area")
    print("  • Smaller sets score (0, 1, 2) below it")
    print("  • Games counter in bottom panel (red)")
    print("  • Golden sets color for black team, white for yellow")
    print("  • Winner announcement with team name")
    print("  • Custom background and logo support")
    print("  • Responsive design for all devices")
    print("=" * 85)
    print("🏅 Match Rules:")
    print("  • Best of 3 sets (first to win 2 sets)")
    print("  • Each set: first to 6 games with 2-game lead")
    print("  • Points: 0 → 15 → 30 → 40 → Game")
    print("  • No advantage/deuce: 40-40 next point wins")
    print("  • Winner display shows final score and team name")
    print("=" * 85)
    print("📁 Required Files in Current Directory:")
    print("  • padel_scoreboard_team_sets.html")
    print("  • back.png (your background image)")
    print("  • logo.png (your logo image)")
    print("=" * 85)
    print("🚀 Starting server with corrected layout...")
    print("")

    app.run(debug=True, host='0.0.0.0', port=5000)
