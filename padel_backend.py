from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Enhanced game state with detailed match tracking
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
    'match_history': [], # Detailed point-by-point history
    'match_start_time': datetime.now().isoformat(),
    'match_end_time': None,
    'last_updated': datetime.now().isoformat()
}

# NEW: Detailed match storage for winner display
match_storage = {
    'match_completed': False,
    'match_data': {
        'winner_team': None,
        'winner_name': None,
        'final_sets_score': None,
        'detailed_sets': [],  # Each set's games score
        'match_duration': None,
        'total_points_won': {'black': 0, 'yellow': 0},
        'total_games_won': {'black': 0, 'yellow': 0},
        'sets_breakdown': [],  # Detailed breakdown for display
        'match_summary': None
    },
    'display_shown': False
}

def add_to_history(action, team, score_before, score_after, game_before, game_after, set_before, set_after):
    """Add detailed action to match history"""
    global game_state

    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,  # 'point', 'game', 'set', 'match'
        'team': team,
        'scores': {
            'before': {'score_1': score_before[0], 'score_2': score_before[1]},
            'after': {'score_1': score_after[0], 'score_2': score_after[1]}
        },
        'games': {
            'before': {'game_1': game_before[0], 'game_2': game_before[1]},
            'after': {'game_1': game_after[0], 'game_2': game_after[1]}
        },
        'sets': {
            'before': {'set_1': set_before[0], 'set_2': set_before[1]},
            'after': {'set_1': set_after[0], 'set_2': set_after[1]}
        }
    }

    game_state['match_history'].append(history_entry)

def calculate_match_statistics():
    """Calculate comprehensive match statistics"""
    global game_state, match_storage

    # Calculate total points won by each team
    black_points = len([h for h in game_state['match_history'] if h['action'] == 'point' and h['team'] == 'black'])
    yellow_points = len([h for h in game_state['match_history'] if h['action'] == 'point' and h['team'] == 'yellow'])

    # Calculate total games won
    black_games = len([h for h in game_state['match_history'] if h['action'] == 'game' and h['team'] == 'black'])
    yellow_games = len([h for h in game_state['match_history'] if h['action'] == 'game' and h['team'] == 'yellow'])

    # Create detailed sets breakdown
    sets_breakdown = []
    for i, set_score in enumerate(game_state['set_history'], 1):
        games = set_score.split('-')
        sets_breakdown.append({
            'set_number': i,
            'black_games': int(games[0]),
            'yellow_games': int(games[1]),
            'set_winner': 'black' if int(games[0]) > int(games[1]) else 'yellow'
        })

    return {
        'total_points': {'black': black_points, 'yellow': yellow_points},
        'total_games': {'black': black_games, 'yellow': yellow_games},
        'sets_breakdown': sets_breakdown
    }

def store_match_data():
    """Store complete match data for winner display"""
    global game_state, match_storage

    if not game_state['match_won'] or not game_state['winner']:
        return

    # Calculate comprehensive statistics
    stats = calculate_match_statistics()

    # Calculate match duration
    start_time = datetime.fromisoformat(game_state['match_start_time'])
    end_time = datetime.fromisoformat(game_state['match_end_time'])
    duration_seconds = int((end_time - start_time).total_seconds())
    duration_minutes = duration_seconds // 60
    duration_text = f"{duration_minutes}m {duration_seconds % 60}s" if duration_minutes > 0 else f"{duration_seconds}s"

    # Create detailed sets display
    sets_display = []
    for breakdown in stats['sets_breakdown']:
        sets_display.append(f"{breakdown['black_games']}-{breakdown['yellow_games']}")

    # Store comprehensive match data
    match_storage['match_completed'] = True
    match_storage['match_data'] = {
        'winner_team': game_state['winner']['team'],
        'winner_name': game_state['winner']['team_name'],
        'final_sets_score': game_state['winner']['final_sets'],
        'detailed_sets': sets_display,
        'match_duration': duration_text,
        'total_points_won': stats['total_points'],
        'total_games_won': stats['total_games'],
        'sets_breakdown': stats['sets_breakdown'],
        'match_summary': create_match_summary(stats, sets_display),
        'timestamp': game_state['match_end_time']
    }
    match_storage['display_shown'] = False

    print(f"✅ Match data stored: {match_storage['match_data']['winner_name']} wins!")
    print(f"📊 Final Score: {match_storage['match_data']['final_sets_score']}")
    print(f"⏱️ Duration: {match_storage['match_data']['match_duration']}")

def create_match_summary(stats, sets_display):
    """Create a readable match summary"""
    sets_text = ", ".join(sets_display)
    return f"Sets: {sets_text} | Points: {stats['total_points']['black']}-{stats['total_points']['yellow']} | Games: {stats['total_games']['black']}-{stats['total_games']['yellow']}"

def wipe_match_storage():
    """Clear match storage after display"""
    global match_storage
    match_storage = {
        'match_completed': False,
        'match_data': {
            'winner_team': None,
            'winner_name': None,
            'final_sets_score': None,
            'detailed_sets': [],
            'match_duration': None,
            'total_points_won': {'black': 0, 'yellow': 0},
            'total_games_won': {'black': 0, 'yellow': 0},
            'sets_breakdown': [],
            'match_summary': None
        },
        'display_shown': False
    }
    print("🧹 Match storage wiped clean")

def check_set_winner():
    """Check if a set is complete and update sets count"""
    global game_state

    # Check if either team won the set (6 games with at least 2-game lead)
    if game_state['game_1'] >= 6 and game_state['game_1'] - game_state['game_2'] >= 2:
        # Black team wins the set
        set_before = (game_state['set_1'], game_state['set_2'])
        game_state['set_1'] += 1
        game_state['set_history'].append(f"{game_state['game_1']}-{game_state['game_2']}")

        # Add set win to history
        add_to_history('set', 'black', 
                      (game_state['score_1'], game_state['score_2']),
                      (0, 0),  # Scores reset after set
                      (game_state['game_1'], game_state['game_2']),
                      (0, 0),  # Games reset after set
                      set_before,
                      (game_state['set_1'], game_state['set_2']))

        game_state['game_1'] = 0
        game_state['game_2'] = 0
        return check_match_winner()

    elif game_state['game_2'] >= 6 and game_state['game_2'] - game_state['game_1'] >= 2:
        # Yellow team wins the set
        set_before = (game_state['set_1'], game_state['set_2'])
        game_state['set_2'] += 1
        game_state['set_history'].append(f"{game_state['game_1']}-{game_state['game_2']}")

        # Add set win to history
        add_to_history('set', 'yellow',
                      (game_state['score_1'], game_state['score_2']),
                      (0, 0),  # Scores reset after set
                      (game_state['game_1'], game_state['game_2']),
                      (0, 0),  # Games reset after set
                      set_before,
                      (game_state['set_1'], game_state['set_2']))

        game_state['game_1'] = 0
        game_state['game_2'] = 0
        return check_match_winner()

    return False

def check_match_winner():
    """Check if the match is complete (first to 2 sets wins)"""
    global game_state

    if game_state['set_1'] >= 2:
        # Black team wins the match
        game_state['match_won'] = True
        game_state['match_end_time'] = datetime.now().isoformat()
        game_state['winner'] = {
            'team': 'black',
            'team_name': 'BLACK TEAM',
            'final_sets': f"{game_state['set_1']}-{game_state['set_2']}",
            'match_summary': ', '.join(game_state['set_history']),
            'total_games_won': sum(int(s.split('-')[0]) for s in game_state['set_history']) + game_state['game_1'],
            'match_duration': calculate_match_duration()
        }

        # Add match win to history
        add_to_history('match', 'black',
                      (game_state['score_1'], game_state['score_2']),
                      (game_state['score_1'], game_state['score_2']),
                      (game_state['game_1'], game_state['game_2']),
                      (game_state['game_1'], game_state['game_2']),
                      (game_state['set_1'], game_state['set_2']),
                      (game_state['set_1'], game_state['set_2']))

        # Store detailed match data
        store_match_data()
        return True

    elif game_state['set_2'] >= 2:
        # Yellow team wins the match
        game_state['match_won'] = True
        game_state['match_end_time'] = datetime.now().isoformat()
        game_state['winner'] = {
            'team': 'yellow',
            'team_name': 'YELLOW TEAM',
            'final_sets': f"{game_state['set_1']}-{game_state['set_2']}",
            'match_summary': ', '.join(game_state['set_history']),
            'total_games_won': sum(int(s.split('-')[1]) for s in game_state['set_history']) + game_state['game_2'],
            'match_duration': calculate_match_duration()
        }

        # Add match win to history
        add_to_history('match', 'yellow',
                      (game_state['score_1'], game_state['score_2']),
                      (game_state['score_1'], game_state['score_2']),
                      (game_state['game_1'], game_state['game_2']),
                      (game_state['game_1'], game_state['game_2']),
                      (game_state['set_1'], game_state['set_2']),
                      (game_state['set_1'], game_state['set_2']))

        # Store detailed match data
        store_match_data()
        return True

    return False

def calculate_match_duration():
    """Calculate match duration in minutes"""
    if game_state['match_end_time']:
        start = datetime.fromisoformat(game_state['match_start_time'])
        end = datetime.fromisoformat(game_state['match_end_time'])
        duration = end - start
        total_minutes = int(duration.total_seconds() / 60)
        return f"{total_minutes} minutes"
    return "In progress"

# Serve the final HTML file with enhanced logo
@app.route('/')
def serve_scoreboard():
    """Serve the final scoreboard with enhanced logo"""
    return send_from_directory('.', 'padel_scoreboard.html')

# Serve static files (images) with better logging
@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files like back.png and logo.png"""
    if os.path.exists(filename):
        print(f"✅ Serving {filename}")
        return send_from_directory('.', filename)
    else:
        print(f"⚠️ File not found: {filename}")
        return f"File {filename} not found", 404

# API endpoint to add point with detailed history tracking
@app.route('/add_point', methods=['POST'])
def add_point():
    """Add a point with complete tennis scoring and detailed history tracking"""
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

        # Store state before the point for history
        score_before = (game_state['score_1'], game_state['score_2'])
        game_before = (game_state['game_1'], game_state['game_2'])
        set_before = (game_state['set_1'], game_state['set_2'])

        if team == 'black':
            # Tennis scoring system: 0, 15, 30, 40, Game
            current_score = game_state['score_1']

            if current_score == 0:
                game_state['score_1'] = 15
                action_type = 'point'
            elif current_score == 15:
                game_state['score_1'] = 30
                action_type = 'point'
            elif current_score == 30:
                game_state['score_1'] = 40
                action_type = 'point'
            elif current_score == 40:
                # Win the game
                game_state['game_1'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0
                action_type = 'game'

                # Check if set is won and potentially match
                match_won = check_set_winner()

            # Increment point counter
            game_state['point_1'] += 1

        elif team == 'yellow':
            # Tennis scoring system for yellow team
            current_score = game_state['score_2']

            if current_score == 0:
                game_state['score_2'] = 15
                action_type = 'point'
            elif current_score == 15:
                game_state['score_2'] = 30
                action_type = 'point'
            elif current_score == 30:
                game_state['score_2'] = 40
                action_type = 'point'
            elif current_score == 40:
                # Win the game
                game_state['game_2'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0
                action_type = 'game'

                # Check if set is won and potentially match
                match_won = check_set_winner()

            # Increment point counter
            game_state['point_2'] += 1

        # Add to detailed history (only if not set/match win, which adds their own history)
        if action_type in ['point', 'game'] and not game_state['match_won']:
            add_to_history(action_type, team,
                          score_before,
                          (game_state['score_1'], game_state['score_2']),
                          game_before,
                          (game_state['game_1'], game_state['game_2']),
                          set_before,
                          (game_state['set_1'], game_state['set_2']))

        game_state['last_updated'] = datetime.now().isoformat()

        # Log the action with detailed match info
        if game_state['match_won']:
            print(f"🏆 MATCH WON by {game_state['winner']['team_name']}!")
            print(f"📊 Detailed match data stored for winner display")
        else:
            print(f"{action_type.title()} won by {team} team.")
            print(f"Current state: {game_state['score_1']}-{game_state['score_2']} | Games: {game_state['game_1']}-{game_state['game_2']} | Sets: {game_state['set_1']}-{game_state['set_2']}")

        # Return response with match storage info
        response_data = {
            'success': True,
            'message': f'Point added to {team} team',
            'game_state': game_state,
            'match_won': game_state['match_won'],
            'winner': game_state['winner'] if game_state['match_won'] else None,
            'match_stored': match_storage['match_completed'] and not match_storage['display_shown']
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error adding point: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# NEW: API endpoint to get stored match data for winner display
@app.route('/get_match_data', methods=['GET'])
def get_match_data():
    """Get detailed match data for winner display"""
    global match_storage

    if not match_storage['match_completed']:
        return jsonify({
            'success': False,
            'error': 'No completed match data available'
        }), 404

    return jsonify({
        'success': True,
        'match_data': match_storage['match_data'],
        'display_shown': match_storage['display_shown']
    })

# NEW: API endpoint to mark match data as displayed and wipe it
@app.route('/mark_match_displayed', methods=['POST'])
def mark_match_displayed():
    """Mark match data as displayed and wipe storage"""
    global match_storage

    if not match_storage['match_completed']:
        return jsonify({
            'success': False,
            'error': 'No match data to mark as displayed'
        }), 400

    match_storage['display_shown'] = True

    # Optional: Wipe immediately or after a delay
    wipe_immediately = request.get_json().get('wipe_immediately', True)

    if wipe_immediately:
        wipe_match_storage()
        message = 'Match data marked as displayed and wiped'
    else:
        message = 'Match data marked as displayed'

    return jsonify({
        'success': True,
        'message': message
    })

# API endpoint to get current complete game state
@app.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current complete game state including sets and winner"""
    response_data = game_state.copy()
    # Add match storage status
    response_data['match_storage_available'] = match_storage['match_completed'] and not match_storage['display_shown']
    return jsonify(response_data)

# Match history endpoint
@app.route('/match_history', methods=['GET'])
def get_match_history():
    """Get detailed match history and statistics"""
    global game_state

    # Calculate statistics
    black_points = len([h for h in game_state['match_history'] if h['action'] == 'point' and h['team'] == 'black'])
    yellow_points = len([h for h in game_state['match_history'] if h['action'] == 'point' and h['team'] == 'yellow'])

    black_games = len([h for h in game_state['match_history'] if h['action'] == 'game' and h['team'] == 'black'])
    yellow_games = len([h for h in game_state['match_history'] if h['action'] == 'game' and h['team'] == 'yellow'])

    black_sets = len([h for h in game_state['match_history'] if h['action'] == 'set' and h['team'] == 'black'])
    yellow_sets = len([h for h in game_state['match_history'] if h['action'] == 'set' and h['team'] == 'yellow'])

    # Match info
    match_info = {
        'start_time': game_state['match_start_time'],
        'end_time': game_state['match_end_time'],
        'duration': calculate_match_duration(),
        'winner': game_state['winner'] if game_state['match_won'] else None,
        'match_completed': game_state['match_won'],
        'total_actions': len(game_state['match_history'])
    }

    # Team statistics
    statistics = {
        'black_team_stats': {
            'points_won': black_points,
            'games_won': black_games,
            'sets_won': black_sets,
            'current_score': game_state['score_1'],
            'current_games': game_state['game_1'],
            'current_sets': game_state['set_1']
        },
        'yellow_team_stats': {
            'points_won': yellow_points,
            'games_won': yellow_games,
            'sets_won': yellow_sets,
            'current_score': game_state['score_2'],
            'current_games': game_state['game_2'],
            'current_sets': game_state['set_2']
        }
    }

    return jsonify({
        'success': True,
        'match_info': match_info,
        'statistics': statistics,
        'detailed_history': game_state['match_history'],
        'set_history': game_state['set_history'],
        'current_state': {
            'score_1': game_state['score_1'],
            'score_2': game_state['score_2'],
            'game_1': game_state['game_1'],
            'game_2': game_state['game_2'],
            'set_1': game_state['set_1'],
            'set_2': game_state['set_2'],
            'match_won': game_state['match_won']
        }
    })

# API endpoint to reset the entire match
@app.route('/reset_match', methods=['POST'])
def reset_match():
    """Reset the entire match including sets and history"""
    global game_state, match_storage

    # Wipe any stored match data first
    wipe_match_storage()

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
        'match_history': [],
        'match_start_time': datetime.now().isoformat(),
        'match_end_time': None,
        'last_updated': datetime.now().isoformat()
    }

    print("🔄 Complete match reset with history and storage cleared")
    return jsonify({
        'success': True,
        'message': 'Match reset successfully',
        'game_state': game_state
    })

# Enhanced health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with file status and match storage"""
    logo_exists = os.path.exists('logo.png')
    back_exists = os.path.exists('back.png')

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'game_state': game_state,
        'match_status': 'completed' if game_state['match_won'] else 'in_progress',
        'history_entries': len(game_state['match_history']),
        'match_storage': {
            'completed': match_storage['match_completed'],
            'displayed': match_storage['display_shown'],
            'available_for_display': match_storage['match_completed'] and not match_storage['display_shown']
        },
        'files': {
            'logo_png': 'found' if logo_exists else 'missing',
            'back_png': 'found' if back_exists else 'missing'
        }
    })

if __name__ == '__main__':
    print("🏓 Starting Complete Padel Scoreboard System...")
    print("=" * 90)

    # Check for image files
    required_files = ['back.png', 'logo.png']
    missing_files = []
    found_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            found_files.append(file)

    if found_files:
        print("✅ Found image files:")
        for file in found_files:
            print(f"   • {file}")

    if missing_files:
        print("⚠️  Missing image files:")
        for file in missing_files:
            print(f"   • {file}")
        print("📝 The scoreboard will use fallback designs for missing images.")

    print("")
    print("🌐 Access the scoreboard at: http://localhost:5000")
    print("📊 COMPLETE: Sets-Only Winner Display System")
    print("🏆 Professional winner screen with sets history table")
    print("📋 Full match tracking with automatic data management")
    print("🧹 Automatic storage wipe after display")
    print("=" * 90)
    print("🔗 Complete API Endpoints:")
    print("  GET  /                     - Serve main scoreboard")
    print("  POST /add_point           - Add point to team")
    print("  GET  /game_state          - Current game state")
    print("  GET  /get_match_data      - Retrieve detailed match data")
    print("  POST /mark_match_displayed- Mark as shown and wipe storage")
    print("  GET  /match_history       - Full match history and stats")
    print("  POST /reset_match         - Reset everything")
    print("  GET  /health              - System status")
    print("=" * 90)
    print("✨ COMPLETE FEATURES:")
    print("  • Professional sets-only winner display")
    print("  • Complete match statistics storage")
    print("  • Tennis scoring system with sets tracking")
    print("  • Automatic data storage and wipe")
    print("  • Beautiful UI with hover effects")
    print("  • Responsive design for all devices")
    print("=" * 90)
    print("🚀 Starting server...")
    print("")

    app.run(debug=True, host='0.0.0.0', port=5000)
