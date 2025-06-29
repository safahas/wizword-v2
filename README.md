# WizWord 🎯

WizWord is an AI-powered word guessing game where players try to guess a hidden word by asking yes/no questions. The game uses advanced AI models to select words and answer questions intelligently.

## Features

- Multiple word categories (difficulty is now fixed per game)
- AI-powered word selection and question answering
- Fun and Wiz modes with strategic scoring system
- Optional nickname-based leaderboard
- Local and cloud storage support
- Mobile and desktop friendly UI

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wizword.git
cd wizword
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_api_key_here

# AWS Configuration (Optional - for cloud storage)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=your_aws_region  # e.g., us-east-1

# Game Configuration
USE_CLOUD_STORAGE=false  # Set to true to use AWS DynamoDB instead of local storage

# SMTP Configuration (for password reset and email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_gmail_app_password  # Use a 16-character Google App Password (no spaces)
```

5. Run the game:
```bash
streamlit run streamlit_app.py
```

## How to Play

1. Configure your game:
   - Word length is chosen randomly for each game (3-10 letters)
   - Select a category (General, Animals, Food, etc.)
   - Pick game mode (Fun or Wiz)
   - Enter an optional nickname

2. Game Modes:
   
   ### Fun Mode
   - No scoring system
   - Ask unlimited questions
   - Make multiple guesses
   - Perfect for learning and practice

   ### Wiz Mode
   - Strategic scoring system:
     - Each question: -5 points
     - Wrong guess: -10 points
     - Correct guess: Base points = Word length × multiplier (see below)
     - Question penalty: Number of questions × 5
     - Final points = max(Base points - Question penalty, 10)
   - Higher scores are better!
   - Be strategic with your questions to minimize penalties

   ### Beat Mode
   - **Time-based challenge:** You have a limited amount of time to guess the word.
   - The timer starts as soon as the game begins.
   - Each question and guess consumes time.
   - The faster you solve the word, the higher your score.
   - If time runs out, the game ends automatically.
   - Designed for speed and quick thinking—perfect for competitive play or practicing under pressure!

3. Asking Questions:
   - Questions must be yes/no format (start with Is, Are, Does, etc.)
   - Questions must end with a question mark
   - Examples:
     - "Is it a type of food?"
     - "Does it contain the letter 'a'?"
     - "Is it something you can find at home?"
     - "Would you use this daily?"

4. Making Guesses:
   - Type your guess when ready
   - Guesses must match the word length for the current game
   - In Wiz mode:
     - Wrong guesses cost 10 points
     - Correct guesses earn points based on word length and questions asked
     - Try to minimize questions to maximize your score!

## Forgot Password / Password Reset

If you forget your password, you can reset it directly from the login screen:

1. Click the **"Forgot Password?"** button on the login tab.
2. Enter your registered email address and click **"Send Temporary Password"**.
3. Check your email for a temporary password (valid for 5 minutes).
4. Enter the temporary password and set a new password in the UI.
5. Log in with your new password.

**Note:**
- The app uses your SMTP settings from `.env` to send password reset emails.
- For Gmail, you must use a [Google App Password](https://support.google.com/accounts/answer/185833?hl=en) (remove spaces when copying to `.env`).
- If you use another provider, update `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASS` accordingly.

## Cloud Deployment

To enable cloud storage with AWS:

1. Create a DynamoDB table named `word_guess_games` with primary key `session_id`
2. Set up AWS credentials in your `.env` file
3. Set `USE_CLOUD_STORAGE=true` in your `.env` file

## Development

The project structure is organized as follows:

```
word_guess_contest_ai/
│
├── streamlit_app.py                  # Main UI interface
├── backend/
│   ├── game_logic.py                 # Game state and scoring
│   ├── word_selector.py              # AI word selection
│   └── session_manager.py            # Session handling
│
├── config/
│   └── openrouter_config.py          # API configuration
│
├── assets/                           # Static assets
├── game_data/                        # Local storage (if used)
├── requirements.txt                  # Dependencies
└── README.md                         # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 