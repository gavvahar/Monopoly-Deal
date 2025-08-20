"""
FastAPI app for Monopoly Deal game.
Handles user login, game play, and admin/database operations.
"""

import os
from os import path
from contextlib import asynccontextmanager
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
)


def initialize():
    """
    Load environment variables and return the directory path
    of the current file.
    """
    load_dotenv(path.join(path.dirname(__file__), "./.envs/nihar.env"))
    return path.dirname(path.realpath(__file__))


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
initialize()


# Helper function to check if user is logged in
def get_current_user(request: Request):
    username = request.session.get("username")
    if not username:
        return None
    return username


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Route for home page, redirects to login."""
    return await login_get(request)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """Handle GET request for login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle user login and start game if credentials are valid."""
    global game_state

    db_user = os.getenv("POSTGRES_USER", "nihar")
    db_pass = os.getenv("POSTGRES_PASSWORD")

    if username == db_user and password == db_pass:
        request.session["username"] = username
        game_state = start_game([username])
        return RedirectResponse(url="/play", status_code=303)

    error_text = "Invalid username or password."
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error_text}
    )


@app.get("/logout")
async def logout(request: Request):
    """Log out the current user."""
    request.session.pop("username", None)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/play", response_class=HTMLResponse)
async def play_get(request: Request):
    """Handle GET request for play page."""
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    if not game_state or not game_state.get("started", False):
        return RedirectResponse(url="/login", status_code=303)

    current_player = game_state["players"][game_state["current_player_idx"]]
    return templates.TemplateResponse(
        "play.html",
        {
            "request": request,
            "game_state": game_state,
            "current_player": current_player,
            "message": "",
        },
    )


@app.post("/play")
async def play_post(
    request: Request,
    action: str = Form(...),
    card_idx: int = Form(None),
):
    """Handle POST request for game actions."""
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)

    if not game_state or not game_state.get("started", False):
        return RedirectResponse(url="/login", status_code=303)

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
            "message": message,
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_get(request: Request):
    """Handle GET request for admin page."""
    try:
        # Get existing users using the database module
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
    message = ""

    try:
        # Get existing users using the database module
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
