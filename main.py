"""
FastAPI app for Monopoly Deal game.
Handles user login, game play, and admin/database operations.
"""

import os
from os import path
from contextlib import asynccontextmanager
from datetime import datetime
import pytz
import pyotp
import qrcode
import io
import base64
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from game import start_game, draw_card, play_card, next_turn
from database import (
    initialize_database,
    get_usernames,
    user_exists,
    create_user,
    get_all_users,
    create_admin_user,
    admin_exists,
)


def initialize():
    """
    Load environment variables and return the directory path
    of the current file.
    Also ensures admin credentials are present in the admin table.
    """
    load_dotenv(path.join(path.dirname(__file__), "./.envs/nihar.env"))
    # Insert admin creds into admin table if not present
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    if admin_user and admin_pass and not admin_exists(admin_user):
        create_admin_user(admin_user, admin_pass)
    return path.dirname(path.realpath(__file__))


def is_business_hours():
    """
    Check if the current time is within business hours (9 AM - 5 PM EST, Monday-Friday).
    Returns True if within business hours, False otherwise.
    """
    # Get current time in EST
    est = pytz.timezone("US/Eastern")
    current_time = datetime.now(est)

    # Check if it's a weekday (Monday=0 to Friday=4)
    # Saturday=5, Sunday=6 should always be available
    weekday = current_time.weekday()
    if weekday >= 5:  # Weekend (Saturday=5, Sunday=6)
        return False

    # Check if it's between 9 AM and 5 PM EST on weekdays
    hour = current_time.hour
    return 9 <= hour < 17  # 9 AM to 4:59 PM (5 PM exclusive)


def get_admin_totp_secret():
    """Get or generate TOTP secret for admin account."""
    totp_secret = os.getenv("ADMIN_TOTP_SECRET")
    if not totp_secret:
        # Generate a new secret if not found
        totp_secret = pyotp.random_base32()
        print(f"Generated new TOTP secret: {totp_secret}")
        print("Please add ADMIN_TOTP_SECRET to your .env file")
    return totp_secret


def validate_admin_totp(totp_code):
    """Validate TOTP code for admin account."""
    if not totp_code or len(totp_code) != 6:
        return False

    totp_secret = get_admin_totp_secret()
    totp = pyotp.TOTP(totp_secret)

    try:
        # Validate the TOTP code (allows 30 second window)
        return totp.verify(totp_code, valid_window=1)
    except Exception:
        return False


def generate_admin_qr_code():
    """Generate QR code for admin TOTP setup."""
    totp_secret = get_admin_totp_secret()
    admin_user = os.getenv("ADMIN_USER", "admin")

    # Create TOTP URI
    totp = pyotp.TOTP(totp_secret)
    provisioning_uri = totp.provisioning_uri(
        name=admin_user, issuer_name="Monopoly Deal Admin"
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for display
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


# Initialize database when the app starts
def init_database():
    """Initialize the database when the app starts."""
    try:
        # Add timeout to database operations
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Database initialization timed out")

        # Set timeout for 5 seconds
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)

        try:
            initialize_database()
            print("Database initialized successfully")
        finally:
            signal.alarm(0)  # Cancel alarm

    except TimeoutError:
        print("Warning: Database initialization timed out after 5 seconds")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


# Use lifespan context manager instead of deprecated on_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("FastAPI application starting up...")
    # Database initialization will happen on first request to avoid startup delays
    print("Database initialization deferred to first request")
    yield
    # Shutdown (if needed)
    print("FastAPI application shutting down...")


# Create the app with lifespan
app = FastAPI(title="Monopoly Deal Game", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="replace_this_with_a_random_secret")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Global game state (same as Flask version)
game_state = None
users = set()
# Session management for multiplayer games
game_sessions = {}  # session_code -> game_state
initialize()


# Session management functions
def generate_session_code():
    """Generate a unique 6-character session code."""
    import string
    import random

    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in game_sessions:
            return code


def create_game_session(creator_username):
    """Create a new game session and return the session code."""
    session_code = generate_session_code()
    game_sessions[session_code] = {
        "players": [creator_username],
        "game_state": None,
        "started": False,
        "max_players": 5,
    }
    return session_code


def join_game_session(session_code, username):
    """Add a player to an existing game session. Returns True if successful."""
    if session_code not in game_sessions:
        return False, "Session not found"

    session = game_sessions[session_code]

    if session["started"]:
        return False, "Game already started"

    if len(session["players"]) >= session["max_players"]:
        return False, "Game is full (max 5 players)"

    if username in session["players"]:
        return False, "You are already in this game"

    session["players"].append(username)
    return True, "Successfully joined game"


def start_game_session(session_code):
    """Start the game for a specific session."""
    if session_code not in game_sessions:
        return False, "Session not found"

    session = game_sessions[session_code]

    if session["started"]:
        return False, "Game already started"

    if len(session["players"]) < 1:
        return False, "Need at least 1 player to start"

    # Start the game with all players in the session
    session["game_state"] = start_game(session["players"])
    session["started"] = True
    return True, "Game started successfully"


def get_session_for_user(username):
    """Find the session that contains the given username."""
    for session_code, session in game_sessions.items():
        if username in session["players"]:
            return session_code, session
    return None, None


# Helper function to check if user is logged in
def get_current_user(request: Request):
    username = request.session.get("username")
    if not username:
        return None
    return username


# Helper function to check if admin is logged in
def get_current_admin(request: Request):
    return request.session.get("admin_username")


def check_business_hours_restriction(request: Request, action_type="host"):
    """
    Check if the current time is within business hours and return response.
    Returns None if access allowed, or HTMLResponse with restriction if blocked.
    Admin bypass is checked via session.

    Args:
        action_type: "host" for hosting/creating sessions (restricted),
                    "join" for joining existing sessions (allowed)
    """
    # Check if admin bypass is active in session
    if request.session.get("admin_bypass"):
        return None

    # During business hours, only restrict hosting actions
    if is_business_hours():
        if action_type == "join":
            # Allow joining existing sessions during business hours
            return None

        # Restrict hosting/creating new sessions during business hours
        # Get current time in EST for display
        est = pytz.timezone("US/Eastern")
        current_time = datetime.now(est).strftime("%I:%M %p EST")

        return templates.TemplateResponse(
            "business_hours.html", {"request": request, "current_time": current_time}
        )
    return None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Route for home page, redirects to login."""
    # Check business hours restriction for hosting (login needed to create sessions)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    return await login_get(request)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """Handle GET request for login page."""
    # Check business hours restriction for hosting (login needed to create sessions)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle user login and redirect to lobby."""
    # Check business hours restriction for hosting (login needed to create sessions)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    db_user = os.getenv("POSTGRES_USER", "nihar")
    db_pass = os.getenv("POSTGRES_PASSWORD")

    if username == db_user and password == db_pass:
        request.session["username"] = username
        return RedirectResponse(url="/lobby", status_code=303)

    error_text = "Invalid username or password."
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error_text}
    )


@app.get("/logout")
async def logout(request: Request):
    """Log out the current user."""
    request.session.pop("username", None)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/admin-bypass")
async def admin_bypass_get(request: Request):
    """Redirect GET requests to admin-bypass to home page."""
    return RedirectResponse(url="/", status_code=303)


@app.post("/admin-bypass")
async def admin_bypass_post(
    request: Request,
    admin_password: str = Form(...),
    totp_code: str = Form(...),
    redirect_url: str = Form("/"),
):
    """Handle admin bypass for business hours restriction with 2FA."""
    admin_pass = os.getenv("ADMIN_PASSWORD")

    # Check password first
    if admin_password != admin_pass:
        est = pytz.timezone("US/Eastern")
        current_time = datetime.now(est).strftime("%I:%M %p EST")

        return templates.TemplateResponse(
            "business_hours.html",
            {
                "request": request,
                "current_time": current_time,
                "error": "Invalid admin password.",
            },
        )

    # Check TOTP code
    if not validate_admin_totp(totp_code):
        est = pytz.timezone("US/Eastern")
        current_time = datetime.now(est).strftime("%I:%M %p EST")

        return templates.TemplateResponse(
            "business_hours.html",
            {
                "request": request,
                "current_time": current_time,
                "error": "Invalid 2FA code. Please check your authenticator app.",
            },
        )

    # Both password and TOTP are valid
    request.session["admin_bypass"] = True
    return RedirectResponse(url=redirect_url, status_code=303)


@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_get(request: Request):
    """Admin login page."""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin-login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle admin login using credentials from .env."""
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    if username == admin_user and password == admin_pass:
        request.session["admin_username"] = username
        return RedirectResponse(url="/admin", status_code=303)
    error_text = "Invalid admin username or password."
    return templates.TemplateResponse(
        "admin_login.html", {"request": request, "error": error_text}
    )


@app.get("/admin-2fa-setup", response_class=HTMLResponse)
async def admin_2fa_setup(request: Request):
    """Admin 2FA setup page."""
    # Only show this if admin is logged in
    if not get_current_admin(request):
        return RedirectResponse(url="/admin-login", status_code=303)

    qr_code = generate_admin_qr_code()
    totp_secret = get_admin_totp_secret()

    return templates.TemplateResponse(
        "admin_2fa_setup.html",
        {"request": request, "qr_code": qr_code, "totp_secret": totp_secret},
    )


@app.get("/admin-logout")
async def admin_logout(request: Request):
    """Log out the current admin."""
    request.session.pop("admin_username", None)
    return RedirectResponse(url="/admin-login", status_code=303)


@app.get("/lobby", response_class=HTMLResponse)
async def lobby_get(request: Request):
    """Handle GET request for lobby page."""
    # Check authentication first
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    # Check business hours restriction for hosting (lobby needed to create sessions)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    # Check if user is already in a session
    session_code, session = get_session_for_user(username)

    return templates.TemplateResponse(
        "lobby.html",
        {
            "request": request,
            "username": username,
            "current_session": session_code,
            "current_session_data": session,
            "message": "",
        },
    )


@app.post("/lobby")
async def lobby_post(
    request: Request,
    action: str = Form(...),
    session_code: str = Form(None),
):
    """Handle POST request for lobby actions."""
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    # Apply business hours restrictions based on action type
    if action in ["create_game", "start_game"]:
        # These actions require hosting permissions - check for business hours
        restriction_response = check_business_hours_restriction(request, "host")
        if restriction_response:
            return restriction_response
    elif action in ["join_game", "leave_game"]:
        # These actions are for joining existing sessions - allow during business hours
        restriction_response = check_business_hours_restriction(request, "join")
        if restriction_response:
            return restriction_response

    message = ""
    current_session_code, current_session = get_session_for_user(username)

    if action == "create_game":
        if current_session_code:
            message = "You are already in a game session"
        else:
            create_game_session(username)
            return RedirectResponse(url="/lobby", status_code=303)

    elif action == "join_game":
        if current_session_code:
            message = "You are already in a game session"
        elif not session_code:
            message = "Please enter a session code"
        else:
            success, msg = join_game_session(session_code.upper(), username)
            message = msg
            if success:
                current_session_code = session_code.upper()
                current_session = game_sessions[current_session_code]

    elif action == "start_game":
        if not current_session_code:
            message = "You are not in any game session"
        else:
            success, msg = start_game_session(current_session_code)
            if success:
                return RedirectResponse(
                    url=f"/play/{current_session_code}", status_code=303
                )
            else:
                message = msg

    elif action == "leave_game":
        if current_session_code:
            session = game_sessions[current_session_code]
            if username in session["players"]:
                session["players"].remove(username)
                # Clean up empty sessions
                if not session["players"]:
                    del game_sessions[current_session_code]
                current_session_code = None
                current_session = None
                message = "Left the game session"
        else:
            message = "You are not in any game session"

    return templates.TemplateResponse(
        "lobby.html",
        {
            "request": request,
            "username": username,
            "current_session": current_session_code,
            "current_session_data": current_session,
            "message": message,
        },
    )


@app.get("/play/{session_code}", response_class=HTMLResponse)
async def play_get(request: Request, session_code: str):
    """Handle GET request for play page with session code."""
    # Allow joining existing game sessions during business hours
    restriction_response = check_business_hours_restriction(request, "join")
    if restriction_response:
        return restriction_response

    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    session_code = session_code.upper()
    if session_code not in game_sessions:
        return RedirectResponse(url="/lobby", status_code=303)

    session = game_sessions[session_code]

    if username not in session["players"]:
        return RedirectResponse(url="/lobby", status_code=303)

    if not session["started"] or not session["game_state"]:
        return RedirectResponse(url="/lobby", status_code=303)

    game_state = session["game_state"]
    current_player = game_state["players"][game_state["current_player_idx"]]

    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "game_state": game_state,
            "current_player": current_player,
            "session_code": session_code,
            "message": "",
        },
    )


@app.post("/play/{session_code}")
async def play_post(
    request: Request,
    session_code: str,
    action: str = Form(...),
    card_idx: int = Form(None),
):
    """Handle POST request for game actions with session code."""
    # Allow playing in existing game sessions during business hours
    restriction_response = check_business_hours_restriction(request, "join")
    if restriction_response:
        return restriction_response

    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    session_code = session_code.upper()
    if session_code not in game_sessions:
        return RedirectResponse(url="/lobby", status_code=303)

    session = game_sessions[session_code]

    if username not in session["players"]:
        return RedirectResponse(url="/lobby", status_code=303)

    if not session["started"] or not session["game_state"]:
        return RedirectResponse(url="/lobby", status_code=303)

    game_state = session["game_state"]
    message = ""

    if action == "draw":
        message = draw_card(game_state)
    elif action == "play":
        if card_idx is not None:
            message = play_card(game_state, card_idx)
    elif action == "end_turn":
        next_turn(game_state)

    current_player = game_state["players"][game_state["current_player_idx"]]
    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "game_state": game_state,
            "current_player": current_player,
            "session_code": session_code,
            "message": message,
        },
    )


# Fallback route for old /play endpoint (redirect to lobby)
@app.get("/play", response_class=HTMLResponse)
async def play_fallback_get(request: Request):
    """Fallback for old /play route - redirect to lobby."""
    # Check business hours restriction for hosting (fallback redirects to lobby)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    return RedirectResponse(url="/lobby", status_code=303)


@app.post("/play")
async def play_fallback_post(request: Request):
    """Fallback for old /play POST route - redirect to lobby."""
    # Check business hours restriction for hosting (fallback redirects to lobby)
    restriction_response = check_business_hours_restriction(request, "host")
    if restriction_response:
        return restriction_response

    return RedirectResponse(url="/lobby", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
async def admin_get(request: Request):
    """Handle GET request for admin page."""
    if not get_current_admin(request):
        return RedirectResponse(url="/admin-login", status_code=303)
    try:
        db_users = set(get_usernames())
    except Exception as e:
        print(f"Database error in admin_get: {e}")
        db_users = set()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "users": db_users, "message": ""}
    )


@app.post("/admin")
async def admin_post(
    request: Request,
    new_username: str = Form(None),
    new_password: str = Form(""),
):
    """Handle POST request for admin page."""
    if not get_current_admin(request):
        return RedirectResponse(url="/admin-login", status_code=303)
    message = ""
    try:
        db_users = set(get_usernames())
        if new_username:
            if user_exists(new_username):
                message = "User already exists."
            else:
                try:
                    create_user(new_username, new_password or "")
                    message = f"User '{new_username}' created."
                    db_users.add(new_username)
                except Exception as e:
                    message = f"Error creating user: {str(e)}"
    except Exception as e:
        print(f"Database error in admin_post: {e}")
        db_users = set()
        message = "Database connection error. Cannot manage users at this time."
    return templates.TemplateResponse(
        "admin.html", {"request": request, "users": db_users, "message": message}
    )


@app.get("/database", response_class=HTMLResponse)
async def database_view(request: Request):
    """Show all users in the database."""
    try:
        users_data = get_all_users()
        return templates.TemplateResponse(
            "database.html", {"request": request, "users_data": users_data}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "database.html", {"request": request, "users_data": [], "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
