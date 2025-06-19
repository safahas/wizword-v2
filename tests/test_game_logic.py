import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import Mock, patch
from backend.game_logic import GameLogic
import streamlit as st

@pytest.fixture
def mock_word_selector():
    selector = Mock()
    selector.select_word.return_value = "mouse"
    selector.answer_question.return_value = (True, "yes")
    selector.verify_guess.side_effect = lambda word, guess: word.lower() == guess.lower()
    return selector

@pytest.fixture
def game():
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
        with patch('backend.game_logic.WordSelector') as mock_selector_class:
            mock_selector = Mock()
            mock_selector.select_word.return_value = "mouse"
            mock_selector.answer_question.return_value = (True, "yes")
            mock_selector.verify_guess.side_effect = lambda word, guess: word.lower() == guess.lower()
            mock_selector_class.return_value = mock_selector
            
            game = GameLogic(word_length=5, subject="Animals", mode="Wiz")
            game.word_selector = mock_selector
            return game

@pytest.mark.unit
def test_game_initialization(game):
    assert len(game.selected_word) == 5
    assert game.subject == "Animals"
    assert game.mode == "Wiz"
    assert game.score == 0
    assert not game.game_over
    assert len(game.questions_asked) == 0

@pytest.mark.unit
def test_ask_question_challenge_mode(game):
    # Correct answer - no points
    is_valid, answer, points = game.ask_question("Is it a mammal?")
    assert is_valid is True
    assert answer == "yes"
    assert points == 0
    assert game.score == 0
    
    # Mock wrong answer - add points
    game.word_selector.answer_question.return_value = (True, "no")
    is_valid, answer, points = game.ask_question("Does it fly?")
    assert is_valid is True
    assert answer == "no"
    assert points == 10
    assert game.score == 10

@pytest.mark.unit
def test_ask_question_fun_mode():
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
        with patch('backend.game_logic.WordSelector') as mock_selector_class:
            mock_selector = Mock()
            mock_selector.select_word.return_value = "mouse"
            mock_selector.answer_question.return_value = (True, "no")
            mock_selector_class.return_value = mock_selector
            
            game = GameLogic(word_length=5, subject="Animals", mode="Fun")
            game.word_selector = mock_selector
            is_valid, answer, points = game.ask_question("Does it fly?")
            assert is_valid is True
            assert answer == "no"
            assert points == 0
            assert game.score == 0

@pytest.mark.unit
def test_make_guess(game):
    # Wrong guess
    success, message, points = game.make_guess("horse")
    assert not success
    assert "Wrong" in message
    assert points == 10
    assert game.score == 10
    assert game.game_over
    
    # Correct guess (new game)
    with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
        with patch('backend.game_logic.WordSelector') as mock_selector_class:
            mock_selector = Mock()
            mock_selector.select_word.return_value = "mouse"
            mock_selector.answer_question.return_value = (True, "yes")
            mock_selector.verify_guess.side_effect = lambda word, guess: word.lower() == guess.lower()
            mock_selector_class.return_value = mock_selector
            
            game = GameLogic(word_length=5, subject="Animals", mode="Wiz")
            game.word_selector = mock_selector
            success, message, points = game.make_guess("mouse")
            assert success
            assert "Correct" in message
            assert points == 0
            assert game.score == 0
            assert game.game_over

@pytest.mark.unit
def test_get_game_summary(game):
    game.ask_question("Is it a mammal?")
    game.ask_question("Does it fly?")
    game.make_guess("horse")
    
    summary = game.get_game_summary()
    assert len(summary["word"]) == 5
    assert summary["subject"] == "Animals"
    assert summary["mode"] == "Wiz"
    assert summary["score"] == game.score
    assert len(summary["questions_asked"]) == 2
    assert summary["game_over"] is True
    assert summary["word"] == "mouse"

@pytest.mark.unit
def test_invalid_questions(game):
    game.word_selector.answer_question.return_value = (False, "invalid")
    is_valid, answer, points = game.ask_question("How many letters?")
    assert not is_valid
    assert answer == "invalid"
    assert points == 0
    assert game.score == 0
    assert len(game.questions_asked) == 0

@pytest.mark.unit
def test_game_state_tracking(game):
    # Track questions
    game.ask_question("Is it a mammal?")
    assert len(game.questions_asked) == 1
    assert game.questions_asked[0]["question"] == "Is it a mammal?"
    assert game.questions_asked[0]["answer"] == "yes"
    
    # Track time
    assert game.start_time is not None
    summary = game.get_game_summary()
    assert "time_taken" in summary
    assert isinstance(summary["time_taken"], float)

@pytest.mark.integration
def test_share_card_integration(game):
    # Play a game
    game.ask_question("Is it a mammal?")
    game.ask_question("Does it fly?")
    game.make_guess("horse")
    
    # Get game summary
    summary = game.get_game_summary()
    
    # Verify summary has all required fields for share card
    required_fields = ["word", "subject", "score", "time_taken", "mode"]
    for field in required_fields:
        assert field in summary
        assert summary[field] is not None
    
    # Verify field types
    assert isinstance(summary["word"], str)
    assert isinstance(summary["subject"], str)
    assert isinstance(summary["score"], int)
    assert isinstance(summary["time_taken"], float)
    assert isinstance(summary["mode"], str)

def test_fun_mode_game_over_main_logic(monkeypatch):
    # Simulate session state
    st.session_state.clear()
    st.session_state.user = {'username': 'testuser'}
    game = GameLogic(word_length=6, subject='general', mode='Fun', nickname='testuser')
    st.session_state.game = game
    st.session_state.game_over = False
    st.session_state.game_summary = None
    st.session_state.just_finished_game = False
    # Set the selected word to a known value
    game.selected_word = 'parade'
    # Simulate a correct guess
    is_correct, message, points = game.make_guess('parade')
    assert is_correct
    # Simulate the display_game logic for Fun mode after correct guess
    if is_correct:
        st.session_state.game_over = True
        st.session_state.game_summary = game.get_game_summary() if hasattr(game, 'get_game_summary') else {}
        st.session_state.just_finished_game = True
    # Save the game object and word for later comparison
    old_game = st.session_state.game
    old_word = st.session_state.game.selected_word
    # Now simulate a rerun and main() logic
    stopped = False
    def fake_stop():
        nonlocal stopped
        stopped = True
    monkeypatch.setattr(st, "stop", fake_stop)
    # Simulate main() top logic
    if st.session_state.get('just_finished_game', False):
        st.session_state.just_finished_game = False
        # Would call display_game_over here
        shown = 'game_over'
        st.stop()
    else:
        shown = 'other'
    assert shown == 'game_over'
    assert stopped is True
    # Ensure the game object and word did not change (no new word loaded)
    assert st.session_state.game is old_game
    assert st.session_state.game.selected_word == old_word 

def test_show_word_penalty_beat_mode():
    from backend.game_logic import GameLogic
    game = GameLogic(word_length=5, subject='general', mode='Beat', nickname='tester')
    game.selected_word = 'apple'  # 5 letters
    game.score = 100
    penalty = game.apply_show_word_penalty()
    assert penalty == -100  # -20 * 5
    assert game.score == 0  # 100 - 100 

def test_show_word_penalty_wiz_mode():
    from backend.game_logic import GameLogic
    game = GameLogic(word_length=6, subject='general', mode='Wiz', nickname='tester')
    game.selected_word = 'banana'  # 6 letters
    game.score = 200
    penalty = game.apply_show_word_penalty()
    assert penalty == -120  # -20 * 6
    assert game.score == 80  # 200 - 120 

def test_show_word_penalty_beat_mode_once():
    from backend.game_logic import GameLogic
    game = GameLogic(word_length=4, subject='general', mode='Beat', nickname='tester')
    game.selected_word = 'pear'  # 4 letters
    game.score = 80
    penalty1 = game.apply_show_word_penalty()
    penalty2 = game.apply_show_word_penalty()
    assert penalty1 == -80  # -20 * 4
    assert penalty2 == 0  # No penalty second time
    assert game.score == 0  # 80 - 80 

def test_show_word_penalty_wiz_mode_once():
    from backend.game_logic import GameLogic
    game = GameLogic(word_length=7, subject='general', mode='Wiz', nickname='tester')
    game.selected_word = 'orchard'  # 7 letters
    game.score = 200
    penalty1 = game.apply_show_word_penalty()
    penalty2 = game.apply_show_word_penalty()
    assert penalty1 == -140  # -20 * 7
    assert penalty2 == 0  # No penalty second time
    assert game.score == 60  # 200 - 140