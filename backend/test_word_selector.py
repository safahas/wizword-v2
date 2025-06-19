# backend/test_word_selector.py
import os
import logging
try:
    from word_selector import WordSelector
except ImportError:
    from backend.word_selector import WordSelector
try:
    from game_logic import GameLogic
except ImportError:
    from backend.game_logic import GameLogic

# Configure logging with a more visible format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

print("[TEST] Starting test_word_selector.py...")

def test_word_selector():
    print("[TEST] Running test_word_selector()...")
    print("Starting WordSelector tests...\n")
    
    # Initialize WordSelector
    selector = WordSelector()
    
    # Check if we're in API or fallback mode
    # api_mode = selector.validate_api_key()
    # print(f"Running in {'API' if api_mode else 'Fallback'} mode\n")

    # Test 1: Word Selection
    print("=== Test 1: Word Selection ===")
    categories = ["animals", "food", "science", "general"]
    lengths = [3, 4, 5]
    
    for category in categories:
        for length in lengths:
            word = selector.select_word(length, category)
            print(f"Selected {length}-letter {category} word: {word}")
        print()

    # Test 2: Hint Generation
    print("\n=== Test 2: Hint Generation ===")
    test_words = [
        ("tiger", "animals"),
        ("pasta", "food"),
        ("laser", "science"),
        ("peace", "general")
    ]
    
    for word, category in test_words:
        print(f"\nTesting hints for '{word}' ({category}):")
        
        # Test regular hint generation (will use API if available)
        try:
            hint = selector.get_semantic_hint(word, category)
            print(f"API/Smart hint: {hint}")
        except Exception as e:
            print(f"API hint failed: {e}")
        
        # Test fallback hint generation
        fallback_hint = selector._get_fallback_semantic_hint(word, category)
        print(f"Fallback hint: {fallback_hint}")

    # Test 3: Question Answering
    print("\n=== Test 3: Question Answering ===")
    test_questions = [
        ("cat", "Does it contain the letter 'a'?"),
        ("dog", "Is it a 3-letter word?"),
        ("fish", "Does it start with 'f'?"),
        ("bird", "Does it end with 'd'?")
    ]
    
    for word, question in test_questions:
        print(f"\nTesting word: '{word}'")
        print(f"Question: {question}")
        
        # Test regular answer (will use API if available)
        try:
            api_answer = selector.answer_question(word, question)
            print(f"API/Smart answer: {api_answer}")
        except Exception as e:
            print(f"API answer failed: {e}")
        
        # Test fallback answer
        fallback_answer = selector._answer_question_fallback(word, question)
        print(f"Fallback answer: {fallback_answer}")

def test_recent_words_limit():
    print("[TEST] Running test_recent_words_limit()...")
    print("\n=== Test 4: Recent Words Limit from .env ===")
    os.environ["RECENT_WORDS_LIMIT"] = "7"  # Set a small limit for test
    selector = WordSelector()
    # Add 10 words
    for i in range(10):
        selector._add_recent_word(f"word{i}")
    recent = selector.get_recently_used_words()
    print(f"Recent words (should be 7): {recent}")
    print(f"Length of recent words list: {len(recent)} (should be 7)")

def test_beat_mode_scoring():
    print("\n=== Test: Beat Mode Scoring and Show Word Penalty ===")
    # Beat mode, Medium, 3-letter word
    game = GameLogic(word_length=3, subject="general", mode="Beat", nickname="testuser", difficulty="Medium")
    print(f"Initial score: {game.score}")
    # Simulate correct guess with 0 questions asked
    guess = game.selected_word
    is_correct, message, points = game.make_guess(guess)
    print(f"Correct guess: {is_correct}, Points awarded: {points}, Final score: {game.score}")
    # Simulate show word penalty on a new word
    game2 = GameLogic(word_length=3, subject="general", mode="Beat", nickname="testuser", difficulty="Medium")
    penalty = game2.apply_show_word_penalty()
    print(f"Show word penalty for 3-letter word: {penalty}, Score after penalty: {game2.score}")

def test_wiz_mode_scoring():
    print("\n=== Test: Wiz Mode Scoring and Show Word Penalty ===")
    # Wiz mode, Medium, 3-letter word
    game = GameLogic(word_length=3, subject="general", mode="Wiz", nickname="testuser", difficulty="Medium")
    print(f"Initial score: {game.score}")
    # Simulate correct guess with 0 questions asked
    guess = game.selected_word
    is_correct, message, points = game.make_guess(guess)
    print(f"Correct guess: {is_correct}, Points awarded: {points}, Final score: {game.score}")
    # Simulate show word penalty on a new word
    game2 = GameLogic(word_length=3, subject="general", mode="Wiz", nickname="testuser", difficulty="Medium")
    penalty = game2.apply_show_word_penalty()
    print(f"Show word penalty for {len(game2.selected_word)}-letter word: {penalty}, Score after penalty: {game2.score}")

def test_beat_mode_time_taken():
    print("\n=== Test: Beat Mode Time Taken Field ===")
    game = GameLogic(word_length=3, subject="general", mode="Beat", nickname="testuser", difficulty="Medium")
    guess = game.selected_word
    is_correct, message, points = game.make_guess(guess)
    summary = game.get_game_summary()
    print(f"Game summary time_taken: {summary['time_taken']} (should be 300)")
    assert summary['time_taken'] == 300, f"Expected time_taken to be 300, got {summary['time_taken']}"

if __name__ == "__main__":
    print("[TEST] __main__ block executing...")
    try:
        test_beat_mode_scoring()
        print("[TEST] Beat mode scoring test completed.")
        test_wiz_mode_scoring()
        print("[TEST] Wiz mode scoring test completed.")
        test_beat_mode_time_taken()
        print("[TEST] Beat mode time_taken test completed.")
    except Exception as e:
        print(f"[TEST] Exception occurred: {e}")
