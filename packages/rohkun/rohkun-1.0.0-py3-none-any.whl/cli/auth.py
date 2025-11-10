"""CLI authentication utilities."""

import json
import os
import stat
import time
import base64
import requests
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timezone
from rich.console import Console

console = Console()

# Import centralized config
from cli.config import get_config

# Get configuration
_config = get_config()
AUTH_FILE = _config.auth_file
DEFAULT_API_URL = _config.api_url
RATE_LIMIT_FILE = AUTH_FILE.parent / "rate_limit.json"

# Rate limiting constants
_MAX_LOGIN_ATTEMPTS = 5
_LOGIN_WINDOW_SECONDS = 300  # 5 minutes


def _secure_file_permissions_atomic(file_path: Path):
    """Set secure file permissions without using umask.
    
    This avoids process-wide umask changes that could affect concurrent operations.
    """
    try:
        if os.name != 'nt':  # Not Windows
            # Set permissions on existing file directly
            if file_path.exists():
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except (OSError, AttributeError):
        # If we can't set permissions, continue
        # This can happen on some systems
        pass


def _decode_jwt_payload(token: str) -> Optional[Dict]:
    """Decode JWT payload without verification (for expiration checking only).
    
    WARNING: This does NOT verify the JWT signature. The server must always
    verify the signature. This is only for client-side expiration checking.
    """
    try:
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError, IndexError, TypeError):
        return None


def _is_api_key(token: str) -> bool:
    """Check if token is an API key (not a JWT)."""
    # API keys start with rk_live_ or rk_test_ and are NOT JWTs (no dots)
    if token.startswith(('rk_live_', 'rk_test_')):
        # API keys don't have JWT structure (no dots separating header.payload.signature)
        if '.' not in token:
            return True
        # If it has dots, check if it's actually a JWT (3 parts)
        parts = token.split('.')
        if len(parts) != 3:
            return True  # Not a valid JWT, so must be API key
        # If it has 3 parts, try to decode - if it fails, it's probably an API key
        # But to be safe, if it starts with rk_live_ or rk_test_ and has 3 parts,
        # it could still be an API key that happens to have dots
        # For now, we'll check if it can be decoded as JWT
        payload = _decode_jwt_payload(token)
        if payload is None:
            return True  # Can't decode as JWT, so it's an API key
    return False


def _is_token_expired(token: str) -> Optional[bool]:
    """Check if JWT token is expired.
    
    Returns:
        True if expired, False if not expired, None if cannot determine
        
    Note: Returns None (cannot determine) as True (expired) for security.
    Caller should treat None as expired to be safe.
    
    API keys never expire, so this returns False for API keys.
    """
    # API keys don't expire - they're not JWTs
    if _is_api_key(token):
        return False
    
    # For JWT tokens, check expiration
    payload = _decode_jwt_payload(token)
    if not payload:
        # Cannot decode - treat as expired for security
        return True
    
    exp = payload.get('exp')
    if not exp:
        # No expiration claim - treat as expired for security
        return True
    
    # exp is Unix timestamp
    try:
        exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return exp_time < now
    except (ValueError, TypeError, OSError, OverflowError):
        # Invalid timestamp - treat as expired for security
        return True


def _validate_token_format(token: str) -> tuple[bool, Optional[str]]:
    """Validate token format more thoroughly."""
    if not token or not isinstance(token, str):
        return False, "Invalid token"
    
    # Check for expected prefixes
    if not token.startswith(('rk_live_', 'rk_test_', 'rk_')):
        return False, "Invalid token format"
    
    # API keys don't need JWT validation
    if _is_api_key(token):
        return True, None
    
    # For JWT tokens, validate structure
    if '.' in token:
        parts = token.split('.')
        if len(parts) != 3:
            return False, "Invalid token structure"
        
        # Check if payload can be decoded (basic validation)
        payload = _decode_jwt_payload(token)
        if payload is None:
            return False, "Invalid token payload"
    
    return True, None


def _load_rate_limit_data() -> Dict:
    """Load rate limit data from persistent storage with corruption detection."""
    if not RATE_LIMIT_FILE.exists():
        return {}
    
    try:
        with open(RATE_LIMIT_FILE, "r") as f:
            content = f.read()
            if not content or not content.strip():
                # Empty file
                return {}
            
            data = json.loads(content)
            # Validate structure
            if not isinstance(data, dict):
                # Corrupted - start fresh
                return {}
            
            # Validate each entry
            for key, value in data.items():
                if not isinstance(key, str) or not isinstance(value, list):
                    # Corrupted entry - start fresh
                    return {}
            
            return data
    except (json.JSONDecodeError, OSError, PermissionError, UnicodeDecodeError):
        # If file is corrupted or unreadable, delete and start fresh
        try:
            RATE_LIMIT_FILE.unlink()
        except OSError:
            pass
    
    return {}


def _save_rate_limit_data(data: Dict):
    """Save rate limit data to persistent storage with atomic write and validation."""
    try:
        RATE_LIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temp file first, then rename (atomic on most systems)
        temp_file = RATE_LIMIT_FILE.with_suffix('.tmp')
        
        # Write and validate
        with open(temp_file, "w") as f:
            json_str = json.dumps(data, indent=2)
            f.write(json_str)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk
        
        # Verify the file was written correctly
        try:
            with open(temp_file, "r") as f:
                json.loads(f.read())  # Validate JSON
        except (json.JSONDecodeError, OSError):
            # Corrupted write - don't replace original
            temp_file.unlink()
            return
        
        # Set permissions before rename
        _secure_file_permissions_atomic(temp_file)
        
        # Atomic rename
        temp_file.replace(RATE_LIMIT_FILE)
        _secure_file_permissions_atomic(RATE_LIMIT_FILE)
    except (OSError, PermissionError):
        # If we can't save, continue without rate limiting
        try:
            if temp_file.exists():
                temp_file.unlink()
        except OSError:
            pass


def _check_rate_limit(identifier: str) -> tuple[bool, Optional[str]]:
    """Check if login attempts are within rate limit (persistent, privacy-aware)."""
    now = time.time()
    
    # Hash identifier for privacy (don't store emails in plaintext)
    import hashlib
    identifier_hash = hashlib.sha256(identifier.lower().encode()).hexdigest()[:16]
    
    # Load rate limit data
    rate_data = _load_rate_limit_data()
    
    # Get attempts for this identifier
    attempts = rate_data.get(identifier_hash, [])
    if not isinstance(attempts, list):
        attempts = []
    
    # Remove old attempts outside the window
    attempts = [t for t in attempts if isinstance(t, (int, float)) and (now - t) < _LOGIN_WINDOW_SECONDS]
    
    if len(attempts) >= _MAX_LOGIN_ATTEMPTS:
        # Calculate remaining time
        oldest_attempt = min(attempts) if attempts else now
        remaining = max(0, int(_LOGIN_WINDOW_SECONDS - (now - oldest_attempt)))
        return False, f"Too many login attempts. Please wait {remaining} seconds."
    
    # Record this attempt
    attempts.append(now)
    rate_data[identifier_hash] = attempts
    
    # Clean up old entries (keep only recent windows)
    cleaned_data = {
        k: [t for t in v if isinstance(t, (int, float)) and (now - t) < _LOGIN_WINDOW_SECONDS * 2]
        for k, v in rate_data.items()
        if isinstance(v, list) and v
    }
    
    # Save updated data
    _save_rate_limit_data(cleaned_data)
    
    return True, None


def get_auth_token() -> Optional[str]:
    """Get stored authentication token."""
    if not AUTH_FILE.exists():
        return None
    
    try:
        # Open with restricted permissions check
        with open(AUTH_FILE, "r") as f:
            data = json.load(f)
            token = data.get("access_token")
            if token and isinstance(token, str):
                # Check expiration - reject if expired (including cannot determine)
                expiration_status = _is_token_expired(token)
                if expiration_status is True:
                    # Token is expired or cannot be validated
                    console.print("[yellow]Stored token has expired or is invalid[/yellow]")
                    clear_auth_token()
                    return None
                # expiration_status is False - token is valid
                return token
    except json.JSONDecodeError:
        # Corrupted file - clear it
        try:
            AUTH_FILE.unlink()
        except OSError:
            pass
    except (PermissionError, FileNotFoundError, OSError):
        # Cannot read file
        pass
    except Exception:
        # Other errors - fail silently
        pass
    
    return None


def save_auth_token(access_token: str, api_url: str = DEFAULT_API_URL):
    """Save authentication token with secure file permissions."""
    if not access_token or not isinstance(access_token, str):
        raise ValueError("Invalid token")
    
    # Validate token format before saving
    is_valid, error_msg = _validate_token_format(access_token)
    if not is_valid:
        raise ValueError("Invalid token format")
    
    try:
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions on directory too (if possible)
        if os.name != 'nt':
            try:
                os.chmod(AUTH_FILE.parent, stat.S_IRWXU)  # 0700 - owner only
            except (OSError, AttributeError):
                pass
        
        # Write to temp file first, then rename (atomic on most systems)
        temp_file = AUTH_FILE.with_suffix('.tmp')
        
        with open(temp_file, "w") as f:
            json.dump({
                "access_token": access_token,
                "api_url": api_url,
                "saved_at": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        # Set secure file permissions before rename
        _secure_file_permissions_atomic(temp_file)
        
        # Atomic rename
        temp_file.replace(AUTH_FILE)
        _secure_file_permissions_atomic(AUTH_FILE)
        
    except PermissionError:
        raise PermissionError("Cannot write auth file (permissions)")
    except OSError as e:
        raise OSError(f"Cannot save auth file: {e}")


def clear_auth_token():
    """Clear stored authentication token."""
    if AUTH_FILE.exists():
        try:
            AUTH_FILE.unlink()
        except OSError:
            pass


def check_auth(api_url: str = DEFAULT_API_URL, offline_mode: bool = False) -> tuple[bool, Optional[str]]:
    """
    Check if user is authenticated.
    
    Args:
        api_url: API URL to validate against
        offline_mode: If True, skip server validation (useful when server is down)
    
    Returns:
        (is_authenticated, token_or_error_message)
    """
    token = get_auth_token()
    
    if not token:
        return False, None
    
    # Validate token format
    is_valid, error_msg = _validate_token_format(token)
    if not is_valid:
        clear_auth_token()
        return False, "Invalid token"
    
    # Check expiration (offline check)
    expiration_status = _is_token_expired(token)
    if expiration_status is True:
        # Token is expired or cannot be validated
        clear_auth_token()
        return False, "Token expired or invalid"
    # expiration_status is False - token is valid
    
    # If offline mode, trust the token format validation
    if offline_mode:
        return True, token
    
    # Verify token is still valid with server
    try:
        response = requests.get(
            f"{api_url}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if response.status_code == 200:
            return True, token
        elif response.status_code == 401:
            # Unauthorized - token is invalid or expired
            clear_auth_token()
            return False, "Authentication failed"
        else:
            # Other error - don't clear token, might be temporary
            return False, "Authentication check failed"
    except requests.exceptions.Timeout:
        console.print("[yellow]Server timeout, using offline authentication[/yellow]")
        return True, token
    except requests.exceptions.ConnectionError:
        console.print("[yellow]Server unavailable, using offline authentication[/yellow]")
        return True, token
    except requests.exceptions.RequestException:
        console.print("[yellow]Server error, using offline authentication[/yellow]")
        return True, token
    except Exception:
        # Unexpected error - fall back to offline
        return True, token


def require_auth(api_url: str = DEFAULT_API_URL) -> str:
    """
    Require authentication, show login link if not authenticated.
    
    Returns:
        Access token
        
    Raises:
        SystemExit if not authenticated and user doesn't want to login
    """
    is_auth, token = check_auth(api_url)
    
    if is_auth and token:
        return token
    
    # Not authenticated - show login prompt
    console.print("\n[bold yellow]! Authentication Required[/bold yellow]")
    console.print("\nYou need to log in to use this feature.")
    
    # Get webapp URL (remove /api if present, or use as-is)
    webapp_url = api_url.rstrip('/')
    if webapp_url.endswith('/api'):
        webapp_url = webapp_url[:-4]
    
    console.print(f"\n[bold cyan]Step 1: Get your token[/bold cyan]")
    console.print(f"   Open in browser: {webapp_url}/user.html")
    console.print(f"   (Or login first: {webapp_url}/login.html)")
    console.print(f"\n[bold cyan]Step 2: Copy the token and run:[/bold cyan]")
    console.print(f"   [bold]rohkun login --token YOUR_TOKEN[/bold]")
    console.print(f"\n[yellow]The token will be shown in the 'CLI Authentication' section on your user page.[/yellow]")
    console.print(f"\n[dim]Alternative: Run 'rohkun login' for interactive login[/dim]")
    
    raise SystemExit(1)


def login_interactive(api_url: str = DEFAULT_API_URL):
    """Interactive login flow with rate limiting."""
    # Check if user already has a token
    existing_token = get_auth_token()
    if existing_token:
        console.print(f"\n[bold yellow]⚠ Warning: You already have a token saved.[/bold yellow]")
        console.print(f"You can only have one token at a time.")
        console.print(f"\nTo replace it, first run: [bold]rohkun logout[/bold]")
        console.print(f"Then run 'rohkun login' again.")
        return False
    
    console.print("\n[bold cyan]Login[/bold cyan]\n")
    
    email = console.input("[cyan]Email:[/cyan] ").strip()
    if not email:
        console.print("[red]Email is required[/red]")
        return False
    
    password = console.input("[cyan]Password:[/cyan] ", password=True)
    if not password:
        console.print("[red]Password is required[/red]")
        return False
    
    # Rate limiting check
    rate_ok, rate_msg = _check_rate_limit(email.lower())
    if not rate_ok:
        console.print(f"\n[red]✗ {rate_msg}[/red]")
        return False
    
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                access_token = data.get("access_token")
                if not access_token:
                    console.print("\n[red]✗ Login failed[/red]")
                    return False
                
                user = data.get("user", {})
                user_email = user.get('email', 'user') if isinstance(user, dict) else 'user'
                
                save_auth_token(access_token, api_url)
                
                console.print(f"\n[green]✓[/green] Logged in as [bold]{user_email}[/bold]")
                console.print(f"[dim]Token saved to {AUTH_FILE}[/dim]")
                return True
            except (KeyError, json.JSONDecodeError, TypeError):
                console.print("\n[red]✗ Login failed[/red]")
                return False
        elif response.status_code == 401:
            console.print(f"\n[red]✗ Login failed: Invalid credentials[/red]")
            return False
        elif response.status_code == 429:
            console.print(f"\n[red]✗ Login failed: Too many requests. Please wait and try again.[/red]")
            return False
        else:
            console.print(f"\n[red]✗ Login failed[/red]")
            return False
            
    except requests.exceptions.Timeout:
        console.print(f"\n[red]✗ Connection timeout[/red]")
        return False
    except requests.exceptions.ConnectionError:
        console.print(f"\n[red]✗ Connection error[/red]")
        return False
    except requests.exceptions.RequestException:
        console.print(f"\n[red]✗ Connection error[/red]")
        return False
    except Exception:
        console.print(f"\n[red]✗ Login failed[/red]")
        return False


def logout():
    """Logout current user and remove stored token."""
    if AUTH_FILE.exists():
        clear_auth_token()
        console.print("[green]✓[/green] Token removed successfully")
        console.print("[dim]Your authentication token has been deleted from this machine.[/dim]")
    else:
        console.print("[yellow]No token found - you're already logged out[/yellow]")
