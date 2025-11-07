"""Authentication commands for Simultaneous CLI."""

import json
import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import typer
from rich.console import Console
from rich.prompt import Prompt
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

console = Console()
auth_app = typer.Typer(name="auth", help="Authentication commands")

# API base URL (can be overridden via env vars for local dev, but defaults work for production)
API_BASE_URL = os.getenv("SIMULTANEOUS_API_URL", "https://simultaneous-api.fly.dev")
FRONTEND_URL = os.getenv("SIMULTANEOUS_FRONTEND_URL", "https://simultaneous.live")

# Token storage location
TOKEN_FILE = Path.home() / ".simultaneous" / "auth.json"
TOKEN_DIR = TOKEN_FILE.parent


def get_supabase_client() -> Client:
    """Get Supabase client instance for CLI.
    
    Returns:
        Supabase client instance
    """
    # Hardcoded Supabase URL and anon key (safe to hardcode - it's public)
    # This allows the CLI to work on any user's computer without requiring env variables
    supabase_url = "https://psizgcphdcmgokrrvxwf.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzaXpnY3BoZGNtZ29rcnJ2eHdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzUxNTQsImV4cCI6MjA3NzYxMTE1NH0.D_GoatTko6fW4ny4ve36Eb2eLEJx9QfdbP5z5U-dR_M"
    
    return create_client(
        supabase_url,
        supabase_key,
        options=ClientOptions(
            auto_refresh_token=True,
            persist_session=True,
        ),
    )


def load_token() -> dict[str, Any] | None:
    """Load stored authentication token.
    
    Returns:
        Token data dictionary or None if not found
    """
    if not TOKEN_FILE.exists():
        return None
    
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_token(token_data: dict[str, Any]) -> None:
    """Save authentication token to file.
    
    Args:
        token_data: Token data dictionary with access_token, refresh_token, user
    """
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    
    # Set restrictive permissions (Unix only)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass  # Windows doesn't support chmod the same way


def clear_token() -> None:
    """Clear stored authentication token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_current_token() -> str | None:
    """Get current access token from storage.
    
    Returns:
        Access token string or None if not authenticated
    """
    token_data = load_token()
    if token_data:
        return token_data.get("access_token")
    return None


@auth_app.command()
def signup(
    email: str = typer.Option(..., prompt=True, help="Email address"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
) -> None:
    """Sign up for a new account."""
    try:
        # Try API first, fallback to Supabase
        try:
            from cli.api_client import APIClient
            api = APIClient()
            console.print(f"[yellow]Signing up with email: {email}[/yellow]")
            
            response = api.signup(email, password)
            
            if response.get("user"):
                console.print("[green]✓ Account created successfully![/green]")
                console.print(f"[dim]User ID: {response.get('user', {}).get('id', 'N/A')}[/dim]")
                
                # If tokens are returned, save them
                if response.get("access_token"):
                    save_token({
                        "access_token": response["access_token"],
                        "refresh_token": response.get("refresh_token", ""),
                        "user": response.get("user", {}),
                    })
                    console.print("[green]✓ You are now signed in![/green]")
                else:
                    console.print("[yellow]⚠ Please check your email to confirm your account.[/yellow]")
            else:
                console.print("[red]✗ Failed to create account[/red]")
                raise typer.Exit(1)
        except ImportError:
            # Fallback to Supabase client
            client = get_supabase_client()
            
            console.print(f"[yellow]Signing up with email: {email}[/yellow]")
            
            response = client.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if response.user:
                console.print("[green]✓ Account created successfully![/green]")
                console.print(f"[dim]User ID: {response.user.id}[/dim]")
                
                if response.session:
                    # Save the session
                    save_token({
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "user": {
                            "id": response.user.id,
                            "email": response.user.email,
                        },
                    })
                    console.print("[green]✓ You are now signed in![/green]")
                else:
                    console.print("[yellow]⚠ Please check your email to confirm your account.[/yellow]")
            else:
                console.print("[red]✗ Failed to create account[/red]")
                raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""
    
    token: str | None = None
    error: str | None = None
    
    def do_GET(self) -> None:
        """Handle GET request for OAuth callback."""
        # Only handle /callback path
        if not self.path.startswith("/callback"):
            self.send_response(404)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")
            return
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Extract token from query parameters
        if "token" in params:
            OAuthCallbackHandler.token = params["token"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Success</title>
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #4CAF50;">✓ Authentication Successful!</h1>
                    <p>You can close this window and return to the CLI.</p>
                </body>
                </html>
                """
            self.wfile.write(success_html.encode('utf-8'))
        elif "error" in params:
            OAuthCallbackHandler.error = params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            error_html = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Error</title>
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">✗ Authentication Failed</h1>
                    <p>{OAuthCallbackHandler.error}</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
                """
            self.wfile.write(error_html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            error_html = """
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Error</title>
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #f44336;">✗ Invalid Request</h1>
                    <p>No token or error parameter found.</p>
                </body>
                </html>
                """
            self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format: str, *args: Any) -> None:
        """Suppress HTTP server logs."""
        pass


def start_oauth_callback_server(port: int = 8765) -> tuple[HTTPServer, str]:
    """Start a local HTTP server to receive OAuth callback.
    
    Args:
        port: Port number for the callback server
        
    Returns:
        Tuple of (server, callback_url)
    """
    # Reset token and error
    OAuthCallbackHandler.token = None
    OAuthCallbackHandler.error = None
    
    # Try to find an available port
    for p in range(port, port + 10):
        try:
            server = HTTPServer(("localhost", p), OAuthCallbackHandler)
            callback_url = f"http://localhost:{p}/callback"
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            return server, callback_url
        except OSError:
            # Port in use, try next
            continue
    
    raise RuntimeError("Could not find an available port for OAuth callback server")


@auth_app.command()
def signin(
    email: str = typer.Option(None, help="Email address (optional, opens browser if not provided)"),
    password: str = typer.Option(None, help="Password (optional, opens browser if not provided)"),
    web: bool = typer.Option(False, "--web", help="Use web-based login flow"),
) -> None:
    """Sign in to your account."""
    try:
        # Use web-based login flow if requested or if credentials not provided
        if web or (not email and not password):
            # Start local callback server
            server, callback_url = start_oauth_callback_server()
            
            console.print("[yellow]Starting OAuth authentication flow...[/yellow]")
            console.print(f"[dim]Callback URL: {callback_url}[/dim]")
            
            # Build login URL with callback
            login_url = f"{FRONTEND_URL}/auth?cli=true&callback={callback_url}"
            
            # Open browser to login page
            try:
                console.print(f"[cyan]Opening browser to: {FRONTEND_URL}/auth[/cyan]")
                webbrowser.open(login_url)
            except Exception:
                console.print(f"[yellow]Could not open browser automatically.[/yellow]")
                console.print(f"[yellow]Please visit: {login_url}[/yellow]")
            
            # Wait for callback (with timeout)
            console.print("\n[yellow]Waiting for authentication...[/yellow]")
            console.print("[dim]Please complete the login in your browser.[/dim]")
            
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while OAuthCallbackHandler.token is None and OAuthCallbackHandler.error is None:
                if time.time() - start_time > timeout:
                    console.print("[red]✗ Authentication timed out[/red]")
                    server.shutdown()
                    # Fall through to API login
                    if not email:
                        email = Prompt.ask("Email")
                    if not password:
                        password = Prompt.ask("Password", password=True)
                    break
                time.sleep(0.5)
            
            # Shutdown server
            server.shutdown()
            
            # Check for error
            if OAuthCallbackHandler.error:
                console.print(f"[red]✗ Authentication failed: {OAuthCallbackHandler.error}[/red]")
                # Fall through to API login
                if not email:
                    email = Prompt.ask("Email")
                if not password:
                    password = Prompt.ask("Password", password=True)
            elif OAuthCallbackHandler.token:
                # Verify token with API
                try:
                    import httpx
                    response = httpx.get(
                        f"{API_BASE_URL}/v1/auth/me",
                        headers={"Authorization": f"Bearer {OAuthCallbackHandler.token}"},
                        timeout=10.0,
                    )
                    if response.is_success:
                        user_data = response.json()
                        save_token({
                            "access_token": OAuthCallbackHandler.token,
                            "refresh_token": "",  # May not be available from web flow
                            "user": user_data.get("user", {}),
                        })
                        console.print("[green]✓ Signed in successfully via web![/green]")
                        console.print(f"[dim]User: {user_data.get('user', {}).get('email', 'Unknown')}[/dim]")
                        return
                    else:
                        console.print("[yellow]⚠ Token validation failed, falling back to API login...[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]⚠ Error validating token: {str(e)}[/yellow]")
                    console.print("[yellow]Falling back to API login...[/yellow]")
                
                # Fall through to API login if token validation failed
                if not email:
                    email = Prompt.ask("Email")
                if not password:
                    password = Prompt.ask("Password", password=True)
            else:
                # Fall through to API login if no token received
                if not email:
                    email = Prompt.ask("Email")
                if not password:
                    password = Prompt.ask("Password", password=True)
        
        # Use API-based login
        try:
            from cli.api_client import APIClient
            api = APIClient()
            
            console.print(f"[yellow]Signing in with email: {email}[/yellow]")
            
            response = api.signin(email, password)
            
            if response.get("access_token") and response.get("user"):
                # Save the session
                save_token({
                    "access_token": response["access_token"],
                    "refresh_token": response.get("refresh_token", ""),
                    "user": response.get("user", {}),
                })
                
                console.print("[green]✓ Signed in successfully![/green]")
                console.print(f"[dim]User: {response.get('user', {}).get('email', 'Unknown')}[/dim]")
            else:
                console.print("[red]✗ Sign in failed[/red]")
                raise typer.Exit(1)
        except ImportError:
            # Fallback to Supabase client
            client = get_supabase_client()
            
            console.print(f"[yellow]Signing in with email: {email}[/yellow]")
            
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if response.session and response.user:
                # Save the session
                save_token({
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "user_metadata": response.user.user_metadata,
                    },
                })
                
                console.print("[green]✓ Signed in successfully![/green]")
                console.print(f"[dim]User: {response.user.email}[/dim]")
            else:
                console.print("[red]✗ Sign in failed[/red]")
                raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@auth_app.command()
def signout() -> None:
    """Sign out from your account."""
    token_data = load_token()
    
    if not token_data:
        console.print("[yellow]⚠ You are not signed in[/yellow]")
        return
    
    try:
        client = get_supabase_client()
        access_token = token_data.get("access_token")
        
        if access_token:
            # Set the session on the client
            client.auth.set_session(access_token, token_data.get("refresh_token", ""))
            client.auth.sign_out()
        
        # Clear local token
        clear_token()
        console.print("[green]✓ Signed out successfully![/green]")
        
    except Exception as e:
        # Even if sign out fails, clear local token
        clear_token()
        console.print(f"[yellow]⚠ Cleared local session: {str(e)}[/yellow]")


@auth_app.command()
def status() -> None:
    """Check authentication status."""
    token_data = load_token()
    
    if not token_data:
        console.print("[yellow]⚠ Not authenticated[/yellow]")
        console.print("[dim]Use 'sim auth signin' to sign in[/dim]")
        return
    
    try:
        client = get_supabase_client()
        access_token = token_data.get("access_token")
        
        if not access_token:
            console.print("[yellow]⚠ Invalid token stored[/yellow]")
            clear_token()
            return
        
        # Verify token by getting user
        client.auth.set_session(access_token, token_data.get("refresh_token", ""))
        user_response = client.auth.get_user(access_token)
        
        if user_response.user:
            user = token_data.get("user", {})
            console.print("[green]✓ Authenticated[/green]")
            console.print(f"[dim]Email: {user.get('email', 'Unknown')}[/dim]")
            console.print(f"[dim]User ID: {user.get('id', 'Unknown')}[/dim]")
        else:
            console.print("[red]✗ Token is invalid[/red]")
            clear_token()
            console.print("[yellow]⚠ Cleared invalid token[/yellow]")
            
    except Exception as e:
        console.print(f"[red]✗ Error verifying token: {str(e)}[/red]")
        console.print("[yellow]⚠ Token may be invalid[/yellow]")


@auth_app.command()
def whoami() -> None:
    """Show current user information."""
    token_data = load_token()
    
    if not token_data:
        console.print("[yellow]⚠ Not authenticated[/yellow]")
        raise typer.Exit(1)
    
    try:
        client = get_supabase_client()
        access_token = token_data.get("access_token")
        
        if not access_token:
            console.print("[red]✗ Invalid token[/red]")
            raise typer.Exit(1)
        
        # Get user info
        client.auth.set_session(access_token, token_data.get("refresh_token", ""))
        user_response = client.auth.get_user(access_token)
        
        if user_response.user:
            user = user_response.user
            console.print("[bold]Current User:[/bold]")
            console.print(f"  Email: [cyan]{user.email}[/cyan]")
            console.print(f"  ID: [dim]{user.id}[/dim]")
            if user.user_metadata:
                console.print(f"  Metadata: [dim]{json.dumps(user.user_metadata, indent=2)}[/dim]")
        else:
            console.print("[red]✗ Failed to get user information[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


