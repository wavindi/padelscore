from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store game state (in production, use a database)
game_state = {
    'score_1': 15,
    'score_2': 30,
    'point_1': 5,
    'point_2': 3,
    'game_1': 1,
    'game_2': 1,
    'last_updated': datetime.now().isoformat()
}

# Serve the HTML file
@app.route('/')
def serve_scoreboard():
    """Serve the main scoreboard HTML file"""
    return send_from_directory('.', 'padel_scoreboard_both_clickable.html')

# API endpoint to add point to any team
@app.route('/add_point', methods=['POST'])
def add_point():
    """Add a point to the specified team using tennis scoring without advantage"""
    global game_state

    try:
        data = request.get_json()
        team = data.get('team', 'black')

        if team == 'black':
            # Tennis scoring system: 0, 15, 30, 40, Game (no advantage)
            current_score = game_state['score_1']

            if current_score == 0:
                game_state['score_1'] = 15
            elif current_score == 15:
                game_state['score_1'] = 30
            elif current_score == 30:
                game_state['score_1'] = 40
            elif current_score == 40:
                # In no-ad scoring, if opponent is also at 40, next point wins
                # Otherwise, just win the game
                game_state['game_1'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0

            # Increment point counter
            game_state['point_1'] += 1

            return jsonify({
                'success': True,
                'message': f'Point added to {team} team',
                'new_score': game_state['score_1'],
                'new_points': game_state['point_1'],
                'game_state': game_state
            })

        elif team == 'yellow':
            # Tennis scoring system for yellow team (no advantage)
            current_score = game_state['score_2']

            if current_score == 0:
                game_state['score_2'] = 15
            elif current_score == 15:
                game_state['score_2'] = 30
            elif current_score == 30:
                game_state['score_2'] = 40
            elif current_score == 40:
                # In no-ad scoring, next point after 40 always wins
                game_state['game_2'] += 1
                game_state['score_1'] = 0
                game_state['score_2'] = 0
                game_state['point_1'] = 0
                game_state['point_2'] = 0

            # Increment point counter
            game_state['point_2'] += 1

            return jsonify({
                'success': True,
                'message': f'Point added to {team} team',
                'new_score': game_state['score_2'],
                'new_points': game_state['point_2'],
                'game_state': game_state
            })

        game_state['last_updated'] = datetime.now().isoformat()

        # Log the action
        print(f"Point added to {team} team. New state: {game_state}")

    except Exception as e:
        print(f"Error adding point: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get current game state
@app.route('/game_state', methods=['GET'])
def get_game_state():
    """Get the current game state"""
    return jsonify(game_state)

# API endpoint to reset the game
@app.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the game to initial state"""
    global game_state
    game_state = {
        'score_1': 0,
        'score_2': 0,
        'point_1': 0,
        'point_2': 0,
        'game_1': 0,
        'game_2': 0,
        'last_updated': datetime.now().isoformat()
    }

    print("Game reset to initial state")
    return jsonify({
        'success': True,
        'message': 'Game reset successfully',
        'game_state': game_state
    })

# API endpoint to update specific scores
@app.route('/update_scores', methods=['POST'])
def update_scores():
    """Update scores manually"""
    global game_state

    try:
        data = request.get_json()

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

        game_state['last_updated'] = datetime.now().isoformat()

        print(f"Scores updated manually: {game_state}")
        return jsonify({
            'success': True,
            'message': 'Scores updated successfully',
            'game_state': game_state
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
        'game_state': game_state
    })

if __name__ == '__main__':
    print("Starting Padel Scoreboard Flask Server (Tennis Scoring - No Advantage)...")
    print("Access the scoreboard at: http://localhost:5000")
    print("Scoring System: Tennis No-Ad (0 → 15 → 30 → 40 → Game)")
    print("No advantage/deuce - whoever reaches 40 and scores next wins immediately")
    print("")
    print("API Endpoints:")
    print("  POST /add_point - Add point to black or yellow team")
    print("  GET  /game_state - Get current game state")
    print("  POST /reset_game - Reset the game")
    print("  POST /update_scores - Update scores manually")
    print("  GET  /health - Health check")
    print("")
    print("Usage:")
    print("  Click LEFT side (black team) to add points to black team")
    print("  Click RIGHT side (yellow team) to add points to yellow team")

    app.run(debug=True, host='0.0.0.0', port=5000)
