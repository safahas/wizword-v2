import json, os
from datetime import datetime

test_game = {
    "session_id": "testuser_20250627_120000",
    "nickname": "testuser",
    "timestamp": datetime.now().isoformat(),
    "word_length": 5,
    "subject": "general",
    "mode": "Wiz",
    "score": 1234,
    "total_points": 1234,
    "questions_count": 3,
    "guesses_made": 1,
    "duration": 42,
    "time_taken": 42,
    "word": "apple",
    "selected_word": "apple",
    "game_over": True
}

os.makedirs('game_data', exist_ok=True)
with open('game_data/test_high_score.json', 'w') as f:
    json.dump(test_game, f, indent=2)
print('Test game record created.')
