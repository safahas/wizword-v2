from dotenv import load_dotenv
import os

# Always use the absolute path to your .env
load_dotenv(dotenv_path="C:/Users/CICD Student/cursor ai agent/game_guess/.env")

import streamlit as st
# Configure Streamlit page with custom theme
st.set_page_config(
    page_title="WizWord - Word Guessing Game",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# WizWord - Word Guessing Game\nTest your deduction skills against AI!"
    }
)
# st.write("🚨 [DEBUG] THIS IS THE REAL streamlit_app.py - TEST MARKER")
from backend.game_logic import GameLogic
import os
import streamlit as st
import json
import re
import time
import random
from backend.monitoring import logger  # Add monitoring logger
from pathlib import Path
from backend.game_logic import GameLogic
from backend.word_selector import WordSelector
from backend.session_manager import SessionManager
from backend.share_card import create_share_card
from backend.share_utils import ShareUtils
from backend.user_auth import register_user, login_user, load_user_profile
import requests



BEAT_MODE_TIMEOUT_MINUTES = 5
RECENT_WORDS_LIMIT = 50



# Inject click sound JS (static directory)
st.markdown("""
<audio id=\"click-sound\" src=\"static/clicksound.mp3\"></audio>
<script>
document.addEventListener('click', function(e) {
    var audio = document.getElementById('click-sound');
    if(audio) {
        audio.currentTime = 0;
        audio.play();
    }
}, true);
</script>
""", unsafe_allow_html=True)

# Initialize ShareUtils
share_utils = ShareUtils()

# Custom CSS for better UI
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700&family=Poppins:wght@700&display=swap" rel="stylesheet">
    <style>
    /* Make all text more visible and bold */
    body, .stApp, .stMarkdown, .stMetricValue, .stMetricLabel, .stTextInput>div>div>input, .stSelectbox>div>div, .stForm, .stButton>button, .stAlert, .streamlit-expanderHeader, .stRadio>div, .stExpander, .stText, .stDataFrame, .stTable, .stCode, .stMetric, h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        color: #222 !important;
        text-shadow: 0 1px 4px rgba(255,255,255,0.15), 0 1px 1px rgba(0,0,0,0.08);
        letter-spacing: 0.01em;
    }
    /* New styles for the split layout */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px;
    }
    [data-testid="column"]:first-child {
        background: rgba(255, 255, 255, 0.08);
    }
    [data-testid="column"]:last-child {
        background: rgba(255, 255, 255, 0.12);
    }
    .instructions h1 {
        color: #ffffff;
        font-size: 2em;
        margin-bottom: 1em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .instructions h3 {
        color: #ffffff;
        font-size: 1.3em;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .instructions ul {
        margin-left: 1.5em;
        margin-bottom: 1.5em;
    }
    .instructions li {
        margin-bottom: 0.5em;
        color: #ffffff;
    }
    /* Main background with sky gradient */
    .stApp {
        background: linear-gradient(135deg, #B5E3FF 0%, #7CB9E8 100%);
        color: white;
    }
    /* Style for all buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: white;
        transition: all 0.3s ease;
        font-weight: bold;
        font-size: 1.1em;
    }
    /* Special styling for Start New Game button */
    .stButton>button:first-child {
        background: linear-gradient(135deg, #6FDFBF 0%, #A8D8F0 100%);
        border: none;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        height: 4em;
        font-size: 1.2em;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    /* Special hover for Start New Game button */
    .stButton>button:first-child:hover {
        background: linear-gradient(135deg, #5ddfb0 0%, #9ed3f0 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    /* Style for text inputs */
    .stTextInput>div>div>input {
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #000000;
        padding: 1em;
        font-weight: 500;
    }
    .stTextInput>div>div>input::placeholder {
        color: rgba(0, 0, 0, 0.5);
    }
    /* Style for alerts and info boxes */
    .stAlert {
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    /* Style for expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    /* Style for metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    /* Style for headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        margin-bottom: 1em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    /* Style for markdown text */
    .stMarkdown {
        color: #ffffff;
    }
    /* Style for forms */
    .stForm {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Style for selectbox */
    .stSelectbox>div>div {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        color: #000000 !important;
    }
    /* Style for selectbox dropdown */
    .stSelectbox>div>div>div {
        background: white !important;
        color: #000000 !important;
    }
    /* Style for selectbox options */
    .stSelectbox>div>div>div>div>div {
        color: #000000 !important;
    }
    /* Style for selectbox label */
    .stSelectbox label {
        color: white !important;
    }
    /* Style for radio buttons */
    .stRadio>div {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Special styling for hint button */
    .stButton>button[data-testid="hint-button"] {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        border: none;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .stButton>button[data-testid="hint-button"]:hover {
        background: linear-gradient(135deg, #FFE44D 0%, #FFB347 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    /* Style for hint section */
    [data-testid="hint-section"] {
        background: rgba(255, 255, 255, 0.2);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 20px;
    }
    /* Style for hint history */
    [data-testid="hint-history"] {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    /* Style for hint text */
    [data-testid="hint-text"] {
        font-size: 1.1em;
        font-weight: 600;
        color: #000000;
        background: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Timer styles */
    .timer {
        font-size: 1.5em;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.1);
        text-align: center;
        margin: 10px 0;
    }
    /* Progress bar styles */
    .progress-bar {
        width: 100%;
        height: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6FDFBF 0%, #A8D8F0 100%);
        transition: width 0.3s ease;
    }
    /* Animation for correct answer */
    @keyframes correct-answer {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .correct-answer {
        animation: correct-answer 0.5s ease;
    }
    /* Animation for wrong answer */
    @keyframes wrong-answer {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
        100% { transform: translateX(0); }
    }
    .wrong-answer {
        animation: wrong-answer 0.5s ease;
    }
    /* Difficulty selector styles */
    .difficulty-selector {
        margin: 20px 0;
        padding: 15px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    /* Timer color variations */
    .timer-normal {
        color: #ffffff;
    }
    .timer-warning {
        color: #FFD700;
    }
    .timer-danger {
        color: #FF6B6B;
    }
    /* Add custom title styling */
    .game-title {
        font-family: 'Baloo 2', 'Poppins', 'Arial Black', Arial, sans-serif !important;
        font-size: 2.7em;
        font-weight: 700;
        letter-spacing: 0.08em;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #4ECDC4 100%);
        color: #fff;
        text-align: center;
        padding: 28px 48px;
        margin: 28px auto 20px auto;
        border-radius: 28px;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.16),
                    inset 0 -10px 0px rgba(0, 0, 0, 0.10);
        -webkit-text-stroke: 2px #222;
        text-stroke: 2px #222;
        text-shadow: 3px 3px 12px rgba(0,0,0,0.22),
                     0 3px 12px rgba(0,0,0,0.13);
        transition: box-shadow 0.2s, background 0.2s;
    }
    .game-title:hover {
        box-shadow: 0 16px 48px rgba(0,0,0,0.22),
                    0 2px 8px rgba(0,0,0,0.10);
        background: linear-gradient(90deg, #FFD93D 0%, #FF6B6B 50%, #4ECDC4 100%);
    }
    .game-title::before {
        content: "⬅️";
        font-size: 0.8em;
        position: static;
        transform: none;
    }
    .game-title::after {
        content: "➡️";
        font-size: 0.8em;
        position: static;
        transform: none;
    }
    @media (max-width: 768px) {
        .game-title {
            font-size: 2em;
            padding: 20px 30px;
            gap: 10px;
        }
        .game-title::before,
        .game-title::after {
            font-size: 0.6em;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state with default values
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "word_length": 5,
        "subject": "general",  # Changed to lowercase to match WordSelector.CATEGORIES
        "mode": "Fun",
        "nickname": "",
        "score": 0,
        "total_points": 0,
        "questions_asked": [],
        "guesses_made": 0,
        "is_game_active": False,
        "game_instance": None,
        "rate_limit_warning": None,
        "is_loading": False,
        "victory_animation": False,
        "error_count": 0,  # Track consecutive errors
        "last_question_time": 0,  # Rate limiting
        "game_over": False,
        "final_guess_made": False,  # New flag to track if final guess was made
        "final_guess_result": None,  # Store the result of final guess
        "show_game_over": False,  # New flag to control game over screen
        "hint_count": 0,  # Track number of hints given
        "previous_hints": []
    }

def is_yes_no_question(question: str) -> tuple[bool, str]:
    """
    Validate if the question is a proper yes/no question.
    Returns (is_valid, error_message)
    """
    if not question:
        return False, "Question cannot be empty!"
    
    # Clean and lowercase the question
    question = question.strip().lower()
    
    # Check length
    if len(question) < 5:
        return False, "Question is too short. Please be more specific."
    
    if len(question) > 200:
        return False, "Question is too long. Please be more concise."
    
    # Check if it ends with a question mark
    if not question.endswith('?'):
        return False, "Question must end with a question mark (?)"
    
    # Common yes/no question starters
    starters = [
        r"^(is|are|does|do|can|could|will|would|has|have|had|should|must|may)",
        r"^(did|was|were)",
    ]
    
    # Check if it starts with yes/no question words
    if not any(re.match(pattern, question) for pattern in starters):
        return False, "Question must start with: Is, Are, Does, Do, Can, etc."
    
    return True, ""

def validate_word_length(length: int) -> tuple[bool, str]:
    """Validate word length with detailed feedback."""
    if not isinstance(length, int):
        return False, "Word length must be a number"
    # Our dictionary only supports 3-10 letter words
    if length < 3:
        return False, "Word length must be at least 3 letters"
    if length > 10:
        return False, "⚠️ Word length cannot exceed 10 letters in the current dictionary"
    return True, ""

def validate_subject(subject: str) -> tuple[bool, str]:
    """Validate the selected subject."""
    valid_categories = ["general", "animals", "food", "places", "science", "tech", "sports",
                       "movies", "music", "brands", "history", "random", "4th_grade"]
    subject = subject.lower()  # Convert to lowercase for comparison
    if subject not in valid_categories:
        return False, f"Invalid subject. Must be one of: {', '.join(valid_categories)}"
    return True, ""

def check_rate_limit() -> tuple[bool, str]:
    """Check if user is asking questions too quickly."""
    current_time = time.time()
    last_question_time = st.session_state.game_state["last_question_time"]
    
    if current_time - last_question_time < 2:  # 2 seconds cooldown
        return False, "Please wait a moment before asking another question"
    return True, ""

def display_rate_limit_warning():
    """Display rate limit warning with enhanced UI."""
    warning = st.session_state.game_state.get("rate_limit_warning")
    if warning:
        if warning["level"] == "error":
            st.error(f"🚫 {warning['message']}")
        else:
            st.warning(f"⚠️ {warning['message']}")

def handle_api_response(response: dict) -> dict:
    """Handle API response and extract rate limit warnings."""
    if "_rate_limit_warning" in response:
        st.session_state.game_state["rate_limit_warning"] = response["_rate_limit_warning"]
        del response["_rate_limit_warning"]
    return response

def display_player_stats():
    """Display player statistics in the sidebar."""
    if st.session_state.game_state["game_instance"] and st.session_state.game_state["nickname"]:
        st.sidebar.markdown("---")
        st.sidebar.header("📊 Your Stats")
        
        player_stats = st.session_state.game_state["game_instance"].get_player_stats()
        if player_stats:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("Total Games", player_stats["total_games"])
                st.metric("Best Score", int(player_stats["best_score"]))
            with col2:
                st.metric("Avg Score", round(player_stats["avg_score"], 1))
                st.metric("Total Time", format_duration(player_stats["total_time"]))
            
            st.sidebar.markdown(f"**Favorite Category:** {player_stats['favorite_category']}")
            
            # Recent games
            if player_stats["recent_games"]:
                st.sidebar.markdown("**Recent Games**")
                for game in player_stats["recent_games"]:
                    st.sidebar.markdown(
                        f"- {game['subject']} ({game['word_length']} letters): "
                        f"Score {game['score']} ({format_duration(game['time_taken'])})"
                    )

def main():
    """Main application entry point."""
    # Handle play again before any game over checks
    if st.session_state.get('play_again', False):
        prev_game = st.session_state.game
        orig_choice = st.session_state.get('original_word_length_choice', 'any')
        # If the original choice was 'any', randomize a new length each time
        if orig_choice == 'any':
            new_length = random.randint(3, 10)
        else:
            new_length = orig_choice
        orig_category = st.session_state.get('original_category_choice', 'any')
        if orig_category == 'any':
            new_category = random.choice(["general", "animals", "food", "places", "science", "tech", "sports", "4th_grade"])
        else:
            new_category = orig_category
        st.session_state.game = GameLogic(
            word_length=new_length,
            subject=new_category,
            mode=prev_game.mode,
            nickname=st.session_state.user['username'],
            difficulty=prev_game.difficulty
        )
        if 'game_state' in st.session_state:
            st.session_state['game_state']['subject'] = new_category
        st.session_state.game_over = False
        st.session_state.game_summary = None
        st.session_state['play_again'] = False
        st.session_state['just_finished_game'] = False
        st.rerun()
    # Display game over screen immediately if just finished
    if st.session_state.get('just_finished_game', False):
        display_game_over(st.session_state.game_summary)
        st.stop()
    # Defensive: Prevent re-initialization of game in Fun mode after game over
    if st.session_state.get('game_over', False) and st.session_state.game and st.session_state.game.mode == 'Fun':
        display_game_over(st.session_state.game_summary)
        st.stop()
    # User authentication state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "login_error" not in st.session_state:
        st.session_state.login_error = ""
    if "register_error" not in st.session_state:
        st.session_state.register_error = ""
    # If not logged in, show login/register UI
    if not st.session_state.user:
        # Show original WizWord banner using .game-title class (no score message)
        st.markdown("<div class='game-title'>WizWord</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-top:-18px; margin-bottom:18px;'>
            <span style='font-size:1.1em; color:#fff; opacity:0.85; letter-spacing:0.04em;'>AI powered word guess game</span>
        </div>
        """, unsafe_allow_html=True)
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            st.subheader("Login to your account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.login_error = ""
                    st.rerun()
                else:
                    st.session_state.login_error = "Invalid email or password."
            if st.session_state.login_error:
                st.error(st.session_state.login_error)
            # Forgot password flow
            if st.button("Forgot Password?"):
                st.session_state.show_forgot_pw = True
            if st.session_state.get("show_forgot_pw"):
                st.info("Enter your email to receive a temporary password.")
                forgot_email = st.text_input("Email for password reset", key="forgot_email")
                if st.button("Send Temporary Password"):
                    from backend.user_auth import forgot_password
                    result = forgot_password(forgot_email)
                    if result:
                        st.success(result)
                        st.session_state.show_forgot_pw = False
                        st.session_state.show_temp_pw_login = True
                        st.session_state.temp_pw_email = forgot_email
                    else:
                        st.error("No account found or failed to send email.")
            # Temp password login flow
            if st.session_state.get("show_temp_pw_login"):
                st.info("Enter the temporary password sent to your email and set a new password.")
                temp_pw = st.text_input("Temporary Password", key="temp_pw")
                new_pw = st.text_input("New Password", type="password", key="new_pw")
                new_pw2 = st.text_input("Confirm New Password", type="password", key="new_pw2")
                if st.button("Reset Password"):
                    from backend.user_auth import validate_temp_password, load_all_users, save_all_users
                    email = st.session_state.get("temp_pw_email")
                    if not email:
                        st.error("Session error. Please try again.")
                    elif not validate_temp_password(email, temp_pw):
                        st.error("Invalid or expired temporary password.")
                    elif new_pw != new_pw2:
                        st.error("Passwords do not match.")
                    elif len(new_pw) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        users = load_all_users()
                        for user in users:
                            if user['email'] == email:
                                import bcrypt
                                user['password_hash'] = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
                        save_all_users(users)
                        st.success("Password reset successful! Please log in.")
                        st.session_state.show_temp_pw_login = False
        with tabs[1]:
            st.subheader("Create a new account")
            reg_email = st.text_input("Email", key="reg_email")
            reg_username = st.text_input("User Name", key="reg_username")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")
            if st.button("Register"):
                if reg_password != reg_password2:
                    st.session_state.register_error = "Passwords do not match."
                else:
                    err = register_user(reg_email, reg_username, reg_password)
                    if err:
                        st.session_state.register_error = err
                    else:
                        st.success("Registration successful! Please log in.")
                        st.session_state.register_error = ""
            if st.session_state.register_error:
                st.error(st.session_state.register_error)
        return
    # If logged in, show welcome and logout
    # Remove the 'Welcome, username!' message from here
    # Continue with game setup and logic
    # Initialize session state
    if "game" not in st.session_state:
        st.session_state.game = None
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "game_summary" not in st.session_state:
        st.session_state.game_summary = None
        
    # Display welcome screen if no game is active
    if not st.session_state.game:
        display_welcome()
        return
        
    # Display game over screen if game is finished
    if st.session_state.get('just_finished_game', False):
        st.session_state.just_finished_game = False
        display_game_over(st.session_state.game_summary)
        return
    if st.session_state.game_over and st.session_state.game_summary:
        display_game_over(st.session_state.game_summary)
        return
        
    # Display active game
    display_game()

def display_welcome():
    """Display the welcome screen and game setup."""
    if st.session_state.get('game'):
        return  # Defensive: never show settings if a game is active
    if not st.session_state.get('user'):
        # Show WizWord banner with only the title (no high score message)
        st.markdown("""
        <div class='wizword-banner'>
          <div class='wizword-banner-title'>WizWord</div>
        </div>
        <style>
        .wizword-banner {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(90deg, #4ECDC4 0%, #FFD93D 100%);
            color: #222;
            padding: 14px 10px 10px 10px;
            margin-bottom: 18px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            font-weight: 700;
        }
        .wizword-banner-title {
            font-family: 'Baloo 2', 'Poppins', 'Arial Black', Arial, sans-serif !important;
            font-size: 2em;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
        return
    # If logged in, show welcome and high score
    st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><b>Welcome, {st.session_state.user['username']}!</b></div>", unsafe_allow_html=True)
    session_manager = SessionManager()
    result = session_manager.get_global_high_score_current_month()
    if result and result.get('nickname'):
        high_score_html = f"""
            <div class='wizword-banner'>
              <div class='wizword-banner-global-score'>
                🌍 Global Highest Score ({result['mode']}, {result['subject'].title()}, This Month): <span style='color:#FF6B6B;'>{result['score']}</span> by <span style='color:#222;'>{result['nickname']}</span>
              </div>
            </div>
            <style>
            .wizword-banner {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(90deg, #4ECDC4 0%, #FFD93D 100%);
                color: #222;
                padding: 8px 10px;
                margin-bottom: 14px;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                font-weight: 700;
            }}
            .wizword-banner-global-score {{
                font-size: 1em;
                margin-top: 2px;
                font-weight: 700;
                text-align: center;
                white-space: normal;
            }}
            </style>
        """
    else:
        high_score_html = """
            <div class='wizword-banner'>
              <div class='wizword-banner-global-score'>
                🌍 No global scores found for this month.
              </div>
            </div>
            <style>
            .wizword-banner {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: linear-gradient(90deg, #4ECDC4 0%, #FFD93D 100%);
                color: #222;
                padding: 8px 10px;
                margin-bottom: 14px;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                font-weight: 700;
            }
            .wizword-banner-global-score {
                font-size: 1em;
                margin-top: 2px;
                font-weight: 700;
                text-align: center;
                white-space: normal;
            }
            </style>
        """   
    st.markdown(high_score_html, unsafe_allow_html=True)
    # --- End WizWord Banner with Global High Score ---
    if st.session_state.get('game'):
        return  # Defensive: never show settings if a game is active
    # Remove the second welcome message here
    st.markdown("<div class='game-title'>WizWord</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; margin-top:-18px; margin-bottom:18px;'>
        <span style='font-size:1.1em; color:#fff; opacity:0.85; letter-spacing:0.04em;'>AI powered word guess game</span>
    </div>
    """, unsafe_allow_html=True)
    # Create two columns
    left_col, right_col = st.columns([1, 1])  # Equal width columns
    # Left column - Game Settings
    with left_col:
        st.markdown("### ⚙️ Game Settings")
        with st.form("game_setup", clear_on_submit=False):
            start_col = st.columns([1])[0]
            start_pressed = start_col.form_submit_button(
                "🎯 Start!" if st.session_state.get('game_mode', 'Fun') == "Wiz" else "🎯 Start Game!",
                use_container_width=True
            )
            cols = st.columns([2, 2])  # [Game Mode, Category]
            with cols[0]:
                mode = st.selectbox(
                    "Game Mode",
                    options=["Fun", "Wiz", "Beat"],
                    help="Wiz mode includes scoring and leaderboards",
                    index=0,
                    key="game_mode"
                )
            difficulty = "Medium"
            with cols[1]:
                subject = st.selectbox(
                    "Category",
                    options=["any", "4th_grade", "general", "animals", "food", "places", "science", "tech", "sports"],
                    index=2,  # Set default to 'general'
                    help="Word category (select 'any' for random category)"
                )
                st.session_state['original_category_choice'] = subject
                resolved_subject = random.choice(["general", "animals", "food", "places", "science", "tech", "sports", "4th_grade"]) if subject == "any" else subject
            word_length = "any"
            st.session_state['original_word_length_choice'] = word_length
            if start_pressed:
                selected_mode = st.session_state.get("game_mode", mode)
                st.session_state.game = GameLogic(
                    word_length=word_length,
                    subject=resolved_subject,
                    mode=selected_mode,
                    nickname=st.session_state.user['username'],
                    difficulty=difficulty
                )
                st.markdown("""
                    <script>
                        window.parent.scrollTo({top: 0, behavior: 'smooth'});
                    </script>
                """, unsafe_allow_html=True)
                st.rerun()
        # End of form block

        # Toggleable High Score Monthly History
        if "show_high_score_history" not in st.session_state:
            st.session_state.show_high_score_history = False

        if st.button("🏆 High Score Monthly History", key="show_high_score_history_btn"):
            st.session_state.show_high_score_history = not st.session_state.show_high_score_history

        if st.session_state.show_high_score_history:
            with st.expander("Global Monthly Highest Score History", expanded=True):
                # Show previous months' high scores for ALL modes and ALL categories
                from datetime import datetime
                session_manager = SessionManager()
                all_games = session_manager._get_local_games()
                year = datetime.now().strftime('%Y')
                monthly_scores = {}
                for g in all_games:
                    ts = g.get('timestamp', '')
                    if g.get('game_over', False) and ts.startswith(year):
                        month = ts[:7]  # YYYY-MM
                        if month not in monthly_scores or g['score'] > monthly_scores[month]['score']:
                            monthly_scores[month] = {
                                'score': g['score'],
                                'nickname': g.get('nickname', ''),
                                'mode': g.get('mode', ''),
                                'subject': g.get('subject', ''),
                            }
                for month in sorted(monthly_scores.keys(), reverse=True):
                    entry = monthly_scores[month]
                    st.markdown(
                        f"**{month}**: 🌍 Global Highest Score ({entry['mode']}, {entry['subject'].title()}): "
                        f"<span style='color:#FF6B6B;'>{entry['score']}</span> by "
                        f"<span style='color:#222;'>{entry['nickname']}</span>",
                        unsafe_allow_html=True
                    )
        # Add Exit button below the form
        if st.button("🚪 Exit", key="exit_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    # Right column - Instructions
    with right_col:
        st.markdown("""
        ### Quick Start 🚀
        1. Select your game mode (Fun, Wiz, or Beat)
        2. Choose a word category (or pick 'any' for random)
        3. Click 'Start Game' to begin!
        """)
        with st.expander("📖 How to Play", expanded=False):
            st.markdown("""
            ### Game Instructions:
            - Choose your game mode:
                - **Fun**: Unlimited play, no timer, just for fun.
                - **Wiz**: Classic mode with stats and leaderboards.
                - **Beat**: Timed challenge—solve as many words as possible before time runs out.
            - Select a word category, or pick 'any' for a random challenge.
            - Ask yes/no questions or request hints to help you guess the word.
            - Enter your guess at any time.
            **Beat Mode Details:**
            - You have 5 minutes to play.
            - For each word, you can:
                - **Guess the word:**
                    - Correct: **+20 × word length**
                    - Wrong: **-10**
                - **Ask yes/no questions:** **-1** each
                - **Request hints:** **-10** each (max 7 per word)
                - **Skip the word:** **-10** (new word loaded)
            - Try to solve as many words as possible and maximize your score before time runs out!
            - Only Medium difficulty is available for all modes.
            """)
        with st.expander("💡 Hints System", expanded=False):
            st.markdown("""
            - Easy Mode: Up to 10 hints available (-5 points each)
            - Medium Mode: Up to 7 hints available (-10 points each)
            - Hard Mode: Up to 5 hints available (-15 points each)
            """)
        with st.expander("🎯 Scoring", expanded=False):
            st.markdown("""
            ### Medium Difficulty (Only Option)
            - 7 hints available per word
            - Questions: **-1** point each
            - Hints: **-10** points each
            - Wrong guesses: **-10** points
            - Skip word: **-10** points (loads a new word)
            - Correct guess: **+20 × word length**
            - 5 minutes to solve as many words as possible in Beat mode
            - Try to maximize your score before time runs out!
            """)
        with st.expander("💭 Tips & Strategy", expanded=False):
            st.markdown("""
            - Use hints strategically—they cost more points than questions
            - In Beat mode, time is limited—work quickly and don't get stuck on one word
            - Keep track of your score before making guesses
            - Questions are cheaper than wrong guesses
            """)

def display_game():
    """Display the active game interface."""
    # Always ensure Beat mode state variables are initialized
    ensure_beat_mode_state()

    if "game" not in st.session_state:
        st.error("No active game found. Please start a new game.")
        return
    game = st.session_state.game
    # Only show and use Beat mode state if in Beat mode
    if game.mode == "Beat":
        ensure_beat_mode_state()
    user_name = st.session_state.user['username'] if st.session_state.get('user') else ''

    max_hints = game.current_settings["max_hints"]

    # --- REMOVE Global Highest Score Banner from running page ---
    # (Banner code removed)
    st.markdown("---")
    # --- END Global Highest Score Banner ---

    # --- BEAT MODE: Defensive initialization before any use ---
    if getattr(game, "mode", None) == "Beat":
        if "beat_word_count" not in st.session_state:
            st.session_state.beat_word_count = 0
        if "beat_score" not in st.session_state:
            st.session_state.beat_score = 0
        if "beat_time_left" not in st.session_state:
            st.session_state.beat_time_left = BEAT_MODE_TIMEOUT_MINUTES * 60
        if "beat_start_time" not in st.session_state:
            st.session_state.beat_start_time = time.time()

    # --- BEAT MODE ---
    if game.mode == "Beat":
        # (Removed st.write for last 25 chosen words)
        # Clear per-word fields when a new word is loaded
        if st.session_state.get("_last_beat_word_count", None) != st.session_state.beat_word_count:
            for key in ("show_word_for_count", "show_word_until"):
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["_last_beat_word_count"] = st.session_state.beat_word_count
            # Clear per-word fields
            st.session_state["last_beat_hint"] = ""
            st.session_state["clear_guess_field"] = True
            st.session_state[f"beat_question_input_{st.session_state.beat_word_count}"] = ""
        elapsed = time.time() - st.session_state.beat_start_time
        time_left = max(0, BEAT_MODE_TIMEOUT_MINUTES * 60 - int(elapsed))
        st.session_state.beat_time_left = time_left
        # --- WIZWORD BANNER (same as Wiz mode) ---
        timer_placeholder = st.empty()
        def render_banner():
            stats_html = f"""
            <div class='wizword-banner'>
              <div class='wizword-banner-title'>WizWord</div>
              <div class='wizword-banner-stats'>
            """
            stats_html += f"<span class='wizword-stat'><b>🎮</b> Beat</span>"
            stats_html += f"<span class='wizword-stat'><b>⏰</b> {time_left // 60}m {time_left % 60}s</span>"
            stats_html += f"<span class='wizword-stat'><b>🏆</b> {st.session_state.beat_score}</span>"
            stats_html += f"<span class='wizword-stat'><b>🔢</b> {st.session_state.beat_word_count}</span>"
            stats_html += "</div></div>"
            stats_html += """
            <style>
            .wizword-banner {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #4ECDC4 100%);
                color: #fff;
                padding: 10px 24px 10px 24px;
                margin: 10px 0 18px 0;
                border-radius: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10),
                            inset 0 -2px 0px rgba(0, 0, 0, 0.07);
                -webkit-text-stroke: 1px #222;
                text-stroke: 1px #222;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.13),
                             0 1px 4px rgba(0,0,0,0.08);
                transition: box-shadow 0.2s, background 0.2s;
            }
            .wizword-banner-title {
                font-family: 'Baloo 2', 'Poppins', 'Arial Black', Arial, sans-serif !important;
                font-size: 1.5em;
                font-weight: 700;
                letter-spacing: 0.08em;
                margin-right: 24px;
                flex: 0 0 auto;
            }
            .wizword-banner-stats {
                display: flex;
                flex-direction: row;
                gap: 18px;
                font-size: 1.1em;
                font-weight: 600;
                align-items: center;
            }
            .wizword-stat {
                background: rgba(0,0,0,0.13);
                border-radius: 8px;
                padding: 4px 12px;
                margin-left: 0;
                margin-right: 0;
                min-width: 60px;
                text-align: center;
                box-shadow: 0 1px 2px rgba(0,0,0,0.07);
            }
            </style>
            """
            timer_placeholder.markdown(stats_html, unsafe_allow_html=True)
        render_banner()
        # --- END FLEX BANNER ---
        # Create main two-column layout (same as Wiz mode)
        left_col, right_col = st.columns([1, 3])
        with left_col:
            st.markdown("### 🎯 Make a Guess")
            actual_length = len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0
            guess_key = f"beat_guess_{st.session_state.beat_word_count}"
            # Only clear the guess field BEFORE widget creation
            if guess_key not in st.session_state or st.session_state.get("clear_guess_field", False):
                st.session_state[guess_key] = ""
                st.session_state["clear_guess_field"] = False
            with st.form(key="beat_guess_form"):
                guess = st.text_input(
                    "Enter your guess:",
                    placeholder=f"Enter a {actual_length}-letter word",
                    help=f"Must be exactly {actual_length} letters",
                    key=guess_key
                )
                submit_guess = st.form_submit_button("Submit Guess", use_container_width=True)
            if submit_guess:
                if not guess:
                    st.error("Please enter a guess!")
                else:
                    is_correct, message, points = game.make_guess(guess)
                    st.session_state.beat_score = game.score
                    if is_correct:
                        st.success(message)
                        st.session_state.beat_word_count += 1
                        st.session_state["clear_guess_field"] = True
                        orig_length = st.session_state.get('original_word_length_choice', len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0)
                        orig_category = st.session_state.get('original_category_choice', game.subject)
                        new_word_length = random.randint(3, 10) if orig_length == "any" else len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0
                        categories = ["general", "animals", "food", "places", "science", "tech", "sports", "4th_grade"]
                        new_subject = random.choice(categories) if orig_category == "any" else game.subject
                        st.session_state.game = GameLogic(
                            word_length=new_word_length,
                            subject=new_subject,
                            mode=game.mode,
                            nickname=game.nickname,
                            difficulty=game.difficulty,
                            initial_score=game.score  # carry over score
                        )
                        st.rerun()
                    else:
                        st.error(message)
                        st.rerun()
            # (Skip and Exit buttons removed from left_col)
        with right_col:
            with st.container():
                display_hint_section(game)
            # Move Show Word button below question field
            is_fallback = game.word_selector.use_fallback
            if is_fallback:
                question_placeholder = "Example: Is the first letter 'A'? (Press Enter to ask)"
                help_text = "In fallback mode, you can only ask about first or last letter"
            else:
                question_placeholder = "Example: Is it used in everyday life? (Press Enter to ask)"
                help_text = "Ask about the word's meaning or properties"
            with st.container():
                question = st.text_input(
                    "Ask a yes/no question about the word:",
                    placeholder=question_placeholder,
                    help=help_text,
                    key=f"beat_question_input_{game.guesses_made}"
                )
                if question:
                    rate_limit_ok, message = check_rate_limit()
                    if not rate_limit_ok:
                        st.warning(message)
                    else:
                        is_valid, answer, points = game.ask_question(question)
                        st.session_state.beat_score = game.score  # Use GameLogic's score
                        if not is_valid:
                            st.warning(answer)
                        else:
                            if points != 0:
                                st.warning(f"{points:+.1f} points", icon="⚠️")
                            st.success(answer)
                            display_rate_limit_warning()
            # Remove any Show Word display logic from here; only display in button row below
            # Place Skip and Exit buttons at the bottom of the right column
            st.markdown("<div style='flex:1 1 auto; min-height:40px;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                # Only use beat_word_count if in Beat mode, else use guesses_made
                word_count = st.session_state.beat_word_count if ("beat_word_count" in st.session_state and game.mode == "Beat") else game.guesses_made
                import time as _time
                # Always render the Show Word button
                if st.button("👀 Show Word", use_container_width=True, key="beat_show_word_btn"):
                    penalty = game.apply_show_word_penalty()
                    st.session_state.show_word_for_count = word_count
                    st.session_state.show_word_until = _time.time() + 10
                    st.warning(f"⚠️ {penalty:+.1f} points penalty for revealing the word!", icon="⚠️")
                    if hasattr(st.session_state, 'beat_score'):
                        st.session_state.beat_score = game.score
                show_word = (
                    st.session_state.get("show_word_for_count", -1) == word_count and
                    st.session_state.get("show_word_until", 0) > _time.time()
                )
                if show_word:
                    st.info(f"Word: **{game.selected_word}**", icon="🤫")
                    _time.sleep(1)
                    st.rerun()
                else:
                    # Clean up stale state if timer expired or word count changed
                    for key in ("show_word_for_count", "show_word_until"):
                        if key in st.session_state:
                            del st.session_state[key]
            with btn_col2:
                # Always ensure Beat mode state before using beat_word_count
                if game.mode == "Beat":
                    ensure_beat_mode_state()
                    # Skip Word button (Beat mode only)
                    if st.button("⏭️", use_container_width=True, key="beat_skip_word_btn"):
                        st.session_state.beat_score -= 10
                        st.session_state.beat_word_count += 1
                        st.session_state["clear_guess_field"] = True
                        st.session_state["last_beat_hint"] = ""
                        st.session_state[f"beat_question_input_{st.session_state.beat_word_count}"] = ""
                        # Remove any show_word or show_word_for_count for the new word
                        for key in ("show_word_for_count", "show_word_until", "show_word"):
                            if key in st.session_state:
                                del st.session_state[key]
                        # --- Load a new word by creating a new GameLogic instance ---
                        game = st.session_state.game
                        orig_length = st.session_state.get('original_word_length_choice', len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0)
                        orig_category = st.session_state.get('original_category_choice', game.subject)
                        new_word_length = random.randint(3, 10) if orig_length == "any" else len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0
                        categories = ["general", "animals", "food", "places", "science", "tech", "sports", "4th_grade"]
                        new_subject = random.choice(categories) if orig_category == "any" else game.subject
                        st.session_state.game = GameLogic(
                            word_length=new_word_length,
                            subject=new_subject,
                            mode=game.mode,
                            nickname=game.nickname,
                            difficulty=game.difficulty,
                            initial_score=st.session_state.beat_score
                        )
                        # (Removed print for last 25 chosen words)
                        print("[DEBUG] New word after skip:", st.session_state.game.selected_word)
                        st.warning("You skipped the word! -10 points.", icon="⚠️")
                        st.rerun()
                # Do not render Skip button in Wiz or Fun mode
                # Restart Game button
                if st.button("🔄 Restart Game", use_container_width=True, key="restart_btn"):
                    reset_game()
                    st.rerun()
                # Logout button (below Restart Game)
                if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                    st.session_state.user = None
                    st.rerun()
        # Timer auto-refresh logic (always rerun every second if not game over)
        if time_left <= 0:
            if not st.session_state.get('game_over', False):
                st.session_state.game_over = True
                st.session_state.game_summary = game.get_game_summary()
                st.session_state.game_summary['game_over'] = True  # Ensure game_over is set
                # Save completed game for global high score (Beat mode timeout)
                SessionManager().save_game(st.session_state.game_summary)
                st.session_state.beat_time_left = 0
                st.session_state.beat_timer_expired = True
                st.rerun()
            else:
                st.info('⏰ Time is up! Game over.')
            return
        # --- Ensure Beat mode game is saved when game_over is set by any means ---
        if st.session_state.get('game_over', False) and st.session_state.get('game_summary'):
            st.session_state.game_summary['game_over'] = True  # Ensure game_over is set
            # Save completed game for global high score (Beat mode manual/other end)
            SessionManager().save_game(st.session_state.game_summary)
            st.session_state.just_finished_game = True
            st.rerun()
        import time as _time
        _time.sleep(1)
        st.rerun()
        return

    print("[DEBUG] Entering legacy UI block (should NOT see this in Beat mode)")
    # Defensive: Beat mode should never reach here
    if game.mode == "Beat":
        st.error("Unexpected: Beat mode should not reach legacy UI block.")
        return
    # --- FLEX BANNER WITH TITLE LEFT, STATS RIGHT ---
    stats_html = """
    <div class='wizword-banner'>
      <div class='wizword-banner-title'>WizWord</div>
      <div class='wizword-banner-stats'>
    """
    stats_html += f"<span class='wizword-stat'><b>🎮</b> {game.mode}</span>"
    if game.mode == "Wiz":
        stats_html += f"<span class='wizword-stat'><b>🏆</b> {game.score}</span>"
        stats_html += f"<span class='wizword-stat'><b>🎯</b> {game.guesses_made}</span>"
        stats_html += f"<span class='wizword-stat'><b>💡</b> {max_hints - len(game.hints_given)}/{max_hints}</span>"
    else:
        stats_html += f"<span class='wizword-stat'><b>🎯</b> {game.guesses_made}</span>"
        stats_html += f"<span class='wizword-stat'><b>💡</b> {max_hints - len(game.hints_given)}/{max_hints}</span>"
    stats_html += "</div></div>"
    stats_html += """
    <style>
    .wizword-banner {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #4ECDC4 100%);
        color: #fff;
        padding: 10px 24px 10px 24px;
        margin: 10px 0 18px 0;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10),
                    inset 0 -2px 0px rgba(0, 0, 0, 0.07);
        -webkit-text-stroke: 1px #222;
        text-stroke: 1px #222;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.13),
                     0 1px 4px rgba(0,0,0,0.08);
        transition: box-shadow 0.2s, background 0.2s;
    }
    .wizword-banner-title {
        font-family: 'Baloo 2', 'Poppins', 'Arial Black', Arial, sans-serif !important;
        font-size: 1.5em;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-right: 24px;
        flex: 0 0 auto;
    }
    .wizword-banner-stats {
        display: flex;
        flex-direction: row;
        gap: 18px;
        font-size: 1.1em;
        font-weight: 600;
        align-items: center;
    }
    .wizword-stat {
        background: rgba(0,0,0,0.13);
        border-radius: 8px;
        padding: 4px 12px;
        margin-left: 0;
        margin-right: 0;
        min-width: 60px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.07);
    }
    </style>
    """
    st.markdown(stats_html, unsafe_allow_html=True)
    # --- END FLEX BANNER ---

    # Create main two-column layout
    left_col, right_col = st.columns([1, 3])  # 1:3 ratio to make right side wider
    
    # Left column - Game Controls
    with left_col:
        st.markdown("### 🎯 Make a Guess")
        actual_length = len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0
        guess_key = f"beat_guess_{game.guesses_made}"  # Use guesses_made for non-Beat modes
        # Only clear the guess field BEFORE widget creation
        if guess_key not in st.session_state or st.session_state.get("clear_guess_field", False):
            st.session_state[guess_key] = ""
            st.session_state["clear_guess_field"] = False
        with st.form(key="beat_guess_form"):
            guess = st.text_input(
                "Enter your guess:",
                placeholder=f"Enter a {actual_length}-letter word",
                help=f"Must be exactly {actual_length} letters",
                key=guess_key
            )
            submit_guess = st.form_submit_button("Submit Guess", use_container_width=True)
        if submit_guess:
            if not guess:
                st.error("Please enter a guess!")
            else:
                is_correct, message, points = game.make_guess(guess)
                st.session_state.beat_score = game.score
                if is_correct:
                    st.success(message)
                    st.session_state.beat_word_count += 1
                    st.session_state["clear_guess_field"] = True
                    orig_length = st.session_state.get('original_word_length_choice', len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0)
                    orig_category = st.session_state.get('original_category_choice', game.subject)
                    new_word_length = random.randint(3, 10) if orig_length == "any" else len(game.selected_word) if hasattr(game, 'selected_word') and game.selected_word else 0
                    categories = ["general", "animals", "food", "places", "science", "tech", "sports", "4th_grade"]
                    new_subject = random.choice(categories) if orig_category == "any" else game.subject
                    st.session_state.game = GameLogic(
                        word_length=new_word_length,
                        subject=new_subject,
                        mode=game.mode,
                        nickname=game.nickname,
                        difficulty=game.difficulty,
                        initial_score=game.score  # carry over score
                    )
                    st.rerun()
                else:
                    st.error(message)
                    st.rerun()
            # (Skip and Exit buttons removed from left_col)

    # Right column - Game Operations
    with right_col:
        # Hint section with combined button
        with st.container():
            display_hint_section(game)
        # Question input - directly in the interface
        is_fallback = game.word_selector.use_fallback
        if is_fallback:
            question_placeholder = "Example: Is the first letter 'A'? (Press Enter to ask)"
            help_text = "In fallback mode, you can only ask about first or last letter"
        else:
            question_placeholder = "Example: Is it used in everyday life? (Press Enter to ask)"
            help_text = "Ask about the word's meaning or properties"
        with st.container():
            question = st.text_input(
                "Ask a yes/no question about the word:",
                placeholder=question_placeholder,
                help=help_text,
                key=f"beat_question_input_{game.guesses_made}"
            )
            if question:
                rate_limit_ok, message = check_rate_limit()
                if not rate_limit_ok:
                    st.warning(message)
                else:
                    is_valid, answer, points = game.ask_question(question)
                    st.session_state.beat_score = game.score  # Use GameLogic's score
                    if not is_valid:
                        st.warning(answer)
                    else:
                        if points != 0:
                            st.warning(f"{points:+.1f} points", icon="⚠️")
                        st.success(answer)
                        display_rate_limit_warning()
        if st.button("🕑 Show All Previous Questions", key="show-history-btn-main"):
            st.session_state.show_history = True
        if st.session_state.get("show_history", False):
            st.markdown("## 📝 All Previous Questions")
            if game.questions_asked:
                for i, qa in enumerate(game.questions_asked, 1):
                    st.write(f"Q{i}: {qa['question']}")
                    st.write(f"A: {qa['answer']}")
                    if game.mode == "Wiz" and qa['points_added'] != 0:
                        st.write(f"Points: {qa['points_added']}")
                    st.divider()
            else:
                st.info("No questions have been asked yet.")
            if st.button("Close History", key="close-history-btn-main"):
                st.session_state.show_history = False
        st.markdown("---")  # Add separator between question and guess sections
        # Place Show Word and Restart Game buttons at the bottom, side by side
        st.markdown("""
            <div style='flex:1 1 auto; min-height:40px;'></div>
            <div style='height:100px;'></div>
            <div style='position: absolute; bottom: 30px; right: 0; width: 90%; z-index: 10;'>
        """, unsafe_allow_html=True)
        btn_cols = st.columns(3)
        with btn_cols[0]:
            # Only use beat_word_count if in Beat mode, else use guesses_made
            word_count = st.session_state.beat_word_count if ("beat_word_count" in st.session_state and game.mode == "Beat") else game.guesses_made
            import time as _time
            # Always render the Show Word button
            if st.button("👀 Show Word", use_container_width=True, key="beat_show_word_btn"):
                penalty = game.apply_show_word_penalty()
                st.session_state.show_word_for_count = word_count
                st.session_state.show_word_until = _time.time() + 10
                st.warning(f"⚠️ {penalty:+.1f} points penalty for revealing the word!", icon="⚠️")
                if hasattr(st.session_state, 'beat_score'):
                    st.session_state.beat_score = game.score
            show_word = (
                st.session_state.get("show_word_for_count", -1) == word_count and
                st.session_state.get("show_word_until", 0) > _time.time()
            )
            if show_word:
                st.info(f"Word: **{game.selected_word}**", icon="🤫")
                _time.sleep(1)
                st.rerun()
            else:
                # Clean up stale state if timer expired or word count changed
                for key in ("show_word_for_count", "show_word_until"):
                    if key in st.session_state:
                        del st.session_state[key]
        with btn_cols[1]:
            # Always ensure Beat mode state before using beat_word_count
            if game.mode == "Beat":
                ensure_beat_mode_state()
                # Skip Word button
                if st.button("⏭️", use_container_width=True, key="beat_skip_word_btn"):
                    st.session_state.beat_score -= 10
                    if game.mode == "Beat":
                        st.session_state.beat_word_count += 1
                    st.session_state["clear_guess_field"] = True
                    st.session_state["last_beat_hint"] = ""
                    if game.mode == "Beat":
                        st.session_state[f"beat_question_input_{st.session_state.beat_word_count}"] = ""
                    # Remove any show_word or show_word_for_count for the new word
                    for key in ("show_word_for_count", "show_word_until", "show_word"):
                        if key in st.session_state:
                            del st.session_state[key]
                    st.warning("You skipped the word! -10 points.", icon="⚠️")
                    st.rerun()
            # Restart Game button
            if st.button("🔄 Restart Game", use_container_width=True, key="restart_btn"):
                reset_game()
                st.rerun()
            # Logout button (below Restart Game)
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.user = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if user_name:
        st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><b>User: {user_name}</b></div>", unsafe_allow_html=True)

def display_game_over(game_summary):
    """Display game over screen with statistics and sharing options."""
    # Add WizWord banner at the top
    stats_html = """
    <div class='wizword-banner'>
      <div class='wizword-banner-title'>WizWord</div>
      <div class='wizword-banner-stats'>
    """
    mode = game_summary.get('mode', 'Fun')
    # Use live Beat score from session state if in Beat mode
    if mode == "Beat":
        score = st.session_state.get('beat_score', 0)
    else:
        score = game_summary.get('score', 0)
    guesses = game_summary.get('guesses_made', len(game_summary.get('questions_asked', [])))
    hints = game_summary.get('max_hints', 7)
    hints_used = len(game_summary.get('hints_given', []))
    stats_html += f"<span class='wizword-stat'><b>🎮</b> {mode}</span>"
    if mode == "Wiz":
        stats_html += f"<span class='wizword-stat'><b>🏆</b> {score}</span>"
        stats_html += f"<span class='wizword-stat'><b>🎯</b> {guesses}</span>"
        stats_html += f"<span class='wizword-stat'><b>💡</b> {hints-hints_used}/{hints}</span>"
    else:
        stats_html += f"<span class='wizword-stat'><b>🎯</b> {guesses}</span>"
        stats_html += f"<span class='wizword-stat'><b>💡</b> {hints-hints_used}/{hints}</span>"
    stats_html += "</div></div>"
    stats_html += """
    <style>
    .wizword-banner {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #4ECDC4 100%);
        color: #fff;
        padding: 10px 24px 10px 24px;
        margin: 10px 0 18px 0;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10),
                    inset 0 -2px 0px rgba(0, 0, 0, 0.07);
        -webkit-text-stroke: 1px #222;
        text-stroke: 1px #222;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.13),
                     0 1px 4px rgba(0,0,0,0.08);
        transition: box-shadow 0.2s, background 0.2s;
    }
    .wizword-banner-title {
        font-family: 'Baloo 2', 'Poppins', 'Arial Black', Arial, sans-serif !important;
        font-size: 1.5em;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-right: 24px;
        flex: 0 0 auto;
    }
    .wizword-banner-stats {
        display: flex;
        flex-direction: row;
        gap: 18px;
        font-size: 1.1em;
        font-weight: 600;
        align-items: center;
    }
    .wizword-stat {
        background: rgba(0,0,0,0.13);
        border-radius: 8px;
        padding: 4px 12px;
        margin-left: 0;
        margin-right: 0;
        min-width: 60px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.07);
    }
    </style>
    """
    st.markdown(stats_html, unsafe_allow_html=True)
    # --- END FLEX BANNER ---
    st.markdown("## 🎉 Game Over!")
    
    # Create tabs for different sections
    summary_tab, stats_tab, share_tab = st.tabs(["Summary", "Statistics", "Share"])
    
    with summary_tab:
        # Game summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Score", score)
        with col2:
            st.metric("Questions Asked", len(game_summary["questions_asked"]))
        with col3:
            st.metric("Time Taken", format_duration(game_summary.get("duration") or game_summary.get("time_taken", 0)))
            
        st.markdown(f"**The word was:** {(game_summary.get('selected_word') or game_summary.get('word', '')).upper()}")
        
        # Question history
        if game_summary["questions_asked"]:
            st.markdown("### Questions Asked")
            for q in game_summary["questions_asked"]:
                st.markdown(f"- Q: {q['question']}\n  A: {q['answer']}")
    
    with stats_tab:
        # Performance graphs
        st.markdown("### Your Performance")
        if st.session_state.game and hasattr(st.session_state.game, 'generate_performance_graphs'):
            graphs = st.session_state.game.generate_performance_graphs()
            
            if graphs:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(graphs["score_distribution"], caption="Score Distribution by Category")
                with col2:
                    st.image(graphs["score_trend"], caption="Score Trend Over Time")
        else:
            st.info("Performance graphs are not available for this game.")
        
        # Leaderboard
        st.markdown("### 🏆 Leaderboard")
        leaderboard_mode = st.selectbox("Game Mode", ["All", "Fun", "Wiz"], key="leaderboard_mode")
        # Convert categories to title case for display
        display_categories = ["All"] + [cat.title() for cat in WordSelector.CATEGORIES]
        category = st.selectbox("Category", display_categories, key="leaderboard_category")
        
        if st.session_state.game and hasattr(st.session_state.game, 'get_leaderboard'):
            leaderboard = st.session_state.game.get_leaderboard(
                leaderboard_mode if leaderboard_mode != "All" else None,
                category.lower() if category != "All" else None  # Convert back to lowercase for backend
            )
            
            if leaderboard:
                for i, entry in enumerate(leaderboard, 1):
                    st.markdown(
                        f"{i}. **{entry['nickname']}** - {entry['score']} points "
                        f"({entry['subject'].title()}, {entry['mode']} mode)"  # Convert subject to title case for display
                    )
            else:
                st.info("No entries in the leaderboard yet!")
        else:
            st.info("Leaderboard is not available for this game.")
        
        # Daily stats
        st.markdown("### 📅 Daily Wiz Stats")
        if st.session_state.game and hasattr(st.session_state.game, 'get_daily_stats'):
            daily_stats = st.session_state.game.get_daily_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Today**")
                st.metric("Games Played", daily_stats["today"]["games_played"])
                st.metric("Total Score", daily_stats["today"]["total_score"])
                if daily_stats["today"]["games_played"] > 0:
                    st.metric("Avg Time", format_duration(daily_stats["today"]["avg_time"]))
            with col2:
                st.markdown("**Yesterday**")
                st.metric("Games Played", daily_stats["yesterday"]["games_played"])
                st.metric("Total Score", daily_stats["yesterday"]["total_score"])
                if daily_stats["yesterday"]["games_played"] > 0:
                    st.metric("Avg Time", format_duration(daily_stats["yesterday"]["avg_time"]))
        else:
            st.info("Daily statistics are not available for this game.")
    
    with share_tab:
        st.markdown("### 🔗 Share Your Achievement!")
        # Generate share card for this game
        if st.button("Generate Share Card"):
            with st.spinner("Generating share card..."):
                game_summary_for_card = dict(game_summary)
                if mode == "Beat":
                    game_summary_for_card["score"] = st.session_state.get('beat_score', 0)
                share_card_path = create_share_card(game_summary_for_card)
                if share_card_path:
                    st.session_state['share_card_path'] = share_card_path
                    st.image(share_card_path, caption="Your Share Card")
                    st.download_button(
                        "Download Share Card",
                        open(share_card_path, "rb"),
                        file_name="word_guess_share.png",
                        mime="image/png"
                    )
        # --- New: Send by Email ---
        if st.session_state.get('share_card_path') and st.session_state.get('user') and st.session_state.user.get('email'):
            unique_id = f"{mode}_{game_summary.get('word','')}"
            share_text = share_utils.generate_share_text(game_summary)
            share_url = share_utils.generate_share_url(game_summary)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Share on Twitter", key=f"share_twitter_btn_sharetab_{unique_id}"):
                    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
                    st.markdown(f"[Click to Tweet]({twitter_url})")
            with col2:
                if st.button("Share on Facebook", key=f"share_facebook_btn_sharetab_{unique_id}"):
                    fb_url = f"https://www.facebook.com/sharer/sharer.php?u={share_url}"
                    st.markdown(f"[Share on Facebook]({fb_url})")
            with col3:
                if st.button("Copy Link", key=f"share_copy_btn_sharetab_{unique_id}"):
                    st.code(share_url)
                    st.success("Link copied to clipboard!")
            with col4:
                email_to = st.session_state.user['email']
                email_subject = "Your WizWord Share Card"
                email_body = "Congratulations! Here is your WizWord share card."
                if st.button("Send Share Card by Email", key=f"share_email_btn_sharetab_{unique_id}"):
                    from backend.user_auth import send_share_card_email
                    print(f"[DEBUG] Attempting to send share card to {email_to} with path {st.session_state['share_card_path']}")
                    with st.spinner("Sending email..."):
                        sent = send_share_card_email(email_to, email_subject, email_body, st.session_state['share_card_path'])
                        if sent:
                            st.success(f"Share card sent to {email_to}!")
                        else:
                            st.error("Failed to send share card by email. Please try again later.")
        # --- NEW: Generate and display highest score share card for this month ---
        from backend.share_card import create_monthly_high_score_share_card
        stats_manager = None
        if hasattr(st.session_state.game, 'stats_manager'):
            stats_manager = st.session_state.game.stats_manager
        if stats_manager and st.button("Show My Highest Score This Month Card"):
            with st.spinner("Generating monthly high score share card..."):
                high_score_card_path = create_monthly_high_score_share_card(stats_manager)
                if high_score_card_path:
                    st.session_state['monthly_high_score_card_path'] = high_score_card_path
                    st.image(high_score_card_path, caption="Your Highest Score This Month")
                    st.download_button(
                        "Download Monthly High Score Card",
                        open(high_score_card_path, "rb"),
                        file_name="monthly_high_score_card.png",
                        mime="image/png"
                    )
                else:
                    st.info("No high score card available for this month.")
        # --- Always show email button if card exists ---
        if st.session_state.get('monthly_high_score_card_path') and st.session_state.get('user') and st.session_state.user.get('email'):
            email_to = st.session_state.user['email']
            email_subject = "Your WizWord Monthly High Score Card"
            email_body = "Congratulations! Here is your WizWord monthly high score card."
            if st.button("Send Monthly High Score Card by Email", key=f"share_email_btn_monthly_{email_to}"):
                from backend.user_auth import send_share_card_email
                print(f"[DEBUG] Attempting to send monthly high score card to {email_to} with path {st.session_state['monthly_high_score_card_path']}")
                with st.spinner("Sending email..."):
                    sent = send_share_card_email(email_to, email_subject, email_body, st.session_state['monthly_high_score_card_path'])
                    if sent:
                        st.success(f"Monthly high score card sent to {email_to}!")
                    else:
                        st.error("Failed to send monthly high score card by email. Please try again later.")
        
        # Share buttons
        share_text = share_utils.generate_share_text(game_summary)
        share_url = share_utils.generate_share_url(game_summary)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Share on Twitter", key="share_twitter_btn_sharetab"):
                twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
                st.markdown(f"[Click to Tweet]({twitter_url})")
        with col2:
            if st.button("Share on Facebook", key="share_facebook_btn_sharetab"):
                fb_url = f"https://www.facebook.com/sharer/sharer.php?u={share_url}"
                st.markdown(f"[Share on Facebook]({fb_url})")
        with col3:
            if st.button("Copy Link", key="share_copy_btn_sharetab"):
                st.code(share_url)
                st.success("Link copied to clipboard!")
    
    # Play again and restart game buttons
    col1, col2 = st.columns(2)
    with col1:
        another_label = '🔄 Another Beat' if mode == 'Beat' else '🔄 Another Word'
        if st.button(another_label, key='play-again-btn'):
            st.session_state['restart_game'] = False
            if mode == 'Beat':
                # Restart Beat mode with same settings
                prev_game = st.session_state.game
                st.session_state.beat_word_count = 0
                st.session_state.beat_score = 0
                st.session_state.beat_time_left = BEAT_MODE_TIMEOUT_MINUTES * 60
                st.session_state.beat_start_time = time.time()
                st.session_state.game = GameLogic(
                    word_length=len(prev_game.selected_word),
                    subject=prev_game.subject,
                    mode=prev_game.mode,
                    nickname=prev_game.nickname,
                    difficulty=prev_game.difficulty
                )
                st.session_state.game_over = False
                st.session_state.game_summary = None
                st.session_state['play_again'] = False
                st.session_state['just_finished_game'] = False
                st.rerun()
            else:
                st.session_state['play_again'] = True
                st.rerun()
    with col2:
        if st.button('🧹 Restart Game', key='restart-game-btn'):
            # Start fresh: clear all session state except user info
            user = st.session_state.get('user')
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            if user:
                st.session_state['user'] = user
            st.rerun()

def reset_game():
    # Clear Beat mode stats
    for key in [
        "beat_word_count", "beat_score", "beat_time_left", "beat_start_time",
        "last_beat_hint", "clear_guess_field", "beat_questions", "beat_hints",
        "beat_guesses", "_last_beat_word_count", "show_word_for_count", "show_word_until", "show_word"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['game'] = None
    if "game_over" in st.session_state:
        del st.session_state.game_over
    if "game_summary" in st.session_state:
        del st.session_state.game_summary

def format_duration(seconds):
    """Format duration in seconds to readable time."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    if minutes == 0:
        return f"{seconds}s"
    return f"{minutes}m {seconds}s"

def display_game_stats(game):
    """Display game statistics."""
    st.markdown("### Game Stats")
    
    # Create columns for stats
    cols = st.columns(5)  # Changed to 5 columns to include difficulty
    
    with cols[0]:
        st.metric("Score", game.score)
    with cols[1]:
        st.metric("Questions Asked", len(game.questions_asked))
    with cols[2]:
        st.metric("Guesses Made", game.guesses_made)
    with cols[3]:
        st.metric("Hints Used", len(game.hints_given))
    with cols[4]:
        st.metric("Difficulty", game.difficulty)
        
    # Display available hints and their status
    st.markdown("### Available Hints")
    max_hints = game.current_settings["max_hints"]  # Get max hints from settings
    for i, hint in enumerate(game.available_hints, 1):
        if i <= max_hints:  # Only show hints up to the difficulty limit
            hint_used = hint in game.hints_given
            status = "✓" if hint_used else "○"
            st.markdown(f"{status} Hint {i}: " + ("*[Used]* " if hint_used else "") + hint)

def display_hint_section(game):
    """Display the hint section."""
    st.markdown("### Get a Hint")
    col1, col2 = st.columns([3, 1])
    
    max_hints = game.current_settings["max_hints"]  # Get max hints from difficulty settings
    hints_remaining = max_hints - len(game.hints_given)
    
    with col1:
        # Show hint button
        if st.button("Get Hint", 
                    disabled=len(game.hints_given) >= max_hints,  # Use max_hints from settings
                    help=f"{hints_remaining} hints remaining",
                    use_container_width=True,
                    key="hint-button"):
            hint, points = game.get_hint()
            if points < 0:
                st.warning(f"Got hint but lost {abs(points)} points!")
            st.info(f"Hint: {hint}")
        # --- Previous Hints Button ---
        if st.button("Previous Hints", key="prev-hints-btn"):
            if game.hints_given:
                st.info("\n".join([f"{i+1}. {h}" for i, h in enumerate(game.hints_given)]), icon="💡")
            else:
                st.info("No previous hints yet.", icon="💡")
    
    with col2:
        st.metric("Hints Left", hints_remaining)  # Use calculated hints remaining

def ensure_beat_mode_state():
    if "beat_word_count" not in st.session_state:
        st.session_state.beat_word_count = 0
    if "beat_score" not in st.session_state:
        st.session_state.beat_score = 0
    if "beat_time_left" not in st.session_state:
        st.session_state.beat_time_left = BEAT_MODE_TIMEOUT_MINUTES * 60
    if "beat_start_time" not in st.session_state:
        st.session_state.beat_start_time = time.time()
    if "last_beat_hint" not in st.session_state:
        st.session_state.last_beat_hint = ""
    if "clear_guess_field" not in st.session_state:
        st.session_state.clear_guess_field = False

if __name__ == "__main__":
    main() 