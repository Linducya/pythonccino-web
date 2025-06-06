<!-- Cleaned up for production: removed debug console.log and commented-out code. -->
# pythonccino-web ☕📚

A web-based book café application built with Python, designed to showcase menu offerings and allow users to browse books and food items. This project is a web adaptation of the **pythonccino** CLI application, transitioning the interactive command-line experience into a user-friendly web interface.

## Features
- Display book and food menus from JSON files
- Simple and responsive HTML interface
- Modular code structure for easy maintenance
- Future plans to integrate MySQL database and Azure cloud storage

## Tech Stack
- Python 3.12
- FastAPI
- Jinja2 Templates
- Google OAuth 2.0 (Gmail API)
- python-jose (JWT)
- bcrypt (password hashing)
- pyotp (TOTP/MFA)
- aiosqlite (async SQLite)
- python-dotenv (env management)
- HTML/CSS (Jinja2 templates)
- JSON for data storage
- Uvicorn (ASGI server)
- (Planned) Azure Storage
- (Planned) MySQL

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/pythonccino-web.git
   cd pythonccino-web
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up Google Cloud Platform OAuth credentials:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and create OAuth 2.0 credentials for a Desktop app.
   - Download the `client_secret_*.json` file and place it in your project root.
   - Set the following environment variables in your `.env` file:
     ```env
     GOOGLE_CLIENT_SECRET_FILE=client_secret_*.json
     GOOGLE_TOKEN_FILE=token.json
     SMTP_EMAIL=your_gmail_address@gmail.com
     ```
   - Run the token generation script (see project docs or scripts) to create `token.json` for Gmail API access.
   - **Never commit your client secret or token files to version control.**
4. Configure other environment variables as needed in `.env` (see sample in repo).
5. Run the application:
   ```sh
   uvicorn main:app --reload
   ```

## OAuth & Email
- This app uses Google OAuth 2.0 for secure email sending via the Gmail API.
- All secrets and tokens are managed via environment variables and are never committed to the repository.

## Security & MFA
- This app uses TOTP-based Multi-Factor Authentication (MFA) at login. After successful TOTP verification, a JWT access token is issued.
- The TOTP code is **not** required for every request—only for initial authentication. All subsequent requests use the JWT for authentication.
- If you want to require TOTP for every sensitive action, you will need to modify both the frontend and backend to pass and verify the TOTP code on each request.
- **Note:** MFA integration and enforcement is still in development. Some endpoints may require further work to fully support secure MFA flows and token handling.

## Roadmap
- [x] Build HTML templates
- [x] Create backend routes
- [ ] Complete MFA (TOTP) integration and enforcement

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## Continuous Integration

This project is ready for GitHub Actions (YAML-based workflows) for automated testing, linting, and deployment.

### Example: Basic Python Test Workflow

Create a file at `.github/workflows/python-app.yml` with the following content:

```yaml
name: Python application

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python test_totp_secret.py
```

- You can add more steps for linting, formatting, or deployment as needed.
- See [GitHub Actions documentation](https://docs.github.com/en/actions) for more details.

## License
This project is licensed under the MIT License.
