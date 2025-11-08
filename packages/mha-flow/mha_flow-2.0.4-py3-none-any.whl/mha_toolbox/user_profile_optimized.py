"""
Thread-Safe Multi-User Profile Management System
=================================================

Optimized for concurrent access by multiple users with session-based isolation.

Key Features:
- Thread-safe file operations with file locking
- Session-based user isolation
- UUID-based session IDs for concurrent users
- Atomic read/write operations
- Automatic cleanup of expired sessions
- In-memory caching for performance

Usage Examples:

1. Web Application (Multi-User):
   from mha_toolbox.user_profile_optimized import create_session_profile
   import uuid
   
   # Create unique session for each user
   session_id = str(uuid.uuid4())
   profile = create_session_profile("alice", session_id=session_id)
   
   # All operations are isolated to this session
   profile.update_preference('mode', 'Professional')
   profile.save()

2. CLI Usage:
   from mha_toolbox.user_profile_optimized import load_profile
   
   # Load user profile (thread-safe)
   profile = load_profile("alice", system_id="workstation-01")

3. Environment Variables:
   export MHA_USER="alice"
   export MHA_SESSION="unique-session-id"
   
   profile = load_profile()  # Auto-loads from environment
"""

import os
import json
import hashlib
import threading
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import getpass
import platform
import time

# Import fcntl only on Unix-like systems (not available on Windows)
try:
    import fcntl
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False


# Global lock for thread-safe operations
_profile_locks = {}
_locks_lock = threading.Lock()


def get_profile_lock(profile_id: str) -> threading.Lock:
    """Get or create a lock for a specific profile."""
    with _locks_lock:
        if profile_id not in _profile_locks:
            _profile_locks[profile_id] = threading.Lock()
        return _profile_locks[profile_id]


@dataclass
class UserProfile:
    """Advanced thread-safe user profile with comprehensive tracking."""
    username: str
    system_id: str
    session_id: str
    user_id: str
    created_at: str
    last_active: str
    total_experiments: int = 0
    total_sessions: int = 0
    preferences: Dict[str, Any] = None
    is_session_based: bool = False
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                # Authentication
                'password_hash': None,
                'created_system': None,
                'last_system': None,
                'system_history': [],
                
                # User Preferences
                'mode': 'Professional',
                'auto_resume': True,
                'auto_update_best': True,
                'save_worse_results': False,
                'theme': 'light',
                'auto_export': False,
                'export_format': 'csv',
                
                # Algorithm Preferences
                'default_algorithms': [],
                'favorite_algorithms': [],
                'default_iterations': 100,
                'default_population': 30,
                'preferred_categories': [],
                
                # Advanced Features
                'notification_email': None,
                'enable_notifications': False,
                'auto_backup': True,
                'max_stored_results': 100,
                
                # Usage Statistics
                'total_runtime_seconds': 0,
                'algorithms_used': {},
                'datasets_processed': 0,
                'best_accuracy_achieved': 0.0,
                'last_10_algorithms': [],
                
                # Security
                'failed_login_attempts': 0,
                'last_login': None,
                'session_timeout_minutes': 60,
            }
    
    def update_preference(self, key: str, value: Any) -> None:
        """Update a single preference."""
        self.preferences[key] = value
        self.last_active = datetime.now().isoformat()
    
    def update_preferences(self, updates: Dict[str, Any]) -> None:
        """Update multiple preferences at once."""
        self.preferences.update(updates)
        self.last_active = datetime.now().isoformat()
    
    def increment_experiments(self) -> None:
        """Increment experiment counter."""
        self.total_experiments += 1
        self.last_active = datetime.now().isoformat()
    
    def increment_sessions(self) -> None:
        """Increment session counter."""
        self.total_sessions += 1
        self.last_active = datetime.now().isoformat()
    
    def track_algorithm_usage(self, algorithm: str, runtime: float, accuracy: float) -> None:
        """Track algorithm usage statistics."""
        # Update algorithm usage count
        algo_stats = self.preferences.get('algorithms_used', {})
        if algorithm in algo_stats:
            algo_stats[algorithm]['count'] += 1
            algo_stats[algorithm]['total_runtime'] += runtime
            algo_stats[algorithm]['avg_accuracy'] = (
                (algo_stats[algorithm]['avg_accuracy'] * (algo_stats[algorithm]['count'] - 1) + accuracy) / 
                algo_stats[algorithm]['count']
            )
        else:
            algo_stats[algorithm] = {
                'count': 1,
                'total_runtime': runtime,
                'avg_accuracy': accuracy
            }
        self.preferences['algorithms_used'] = algo_stats
        
        # Update last 10 algorithms
        last_10 = self.preferences.get('last_10_algorithms', [])
        last_10.insert(0, algorithm)
        self.preferences['last_10_algorithms'] = last_10[:10]
        
        # Update total runtime
        self.preferences['total_runtime_seconds'] = self.preferences.get('total_runtime_seconds', 0) + runtime
        
        # Update best accuracy
        if accuracy > self.preferences.get('best_accuracy_achieved', 0.0):
            self.preferences['best_accuracy_achieved'] = accuracy
        
        self.last_active = datetime.now().isoformat()
    
    def track_system_change(self, new_system: str) -> None:
        """Track system changes for security."""
        system_history = self.preferences.get('system_history', [])
        system_history.append({
            'system': new_system,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        })
        self.preferences['system_history'] = system_history[-20:]  # Keep last 20
        self.preferences['last_system'] = new_system
        self.last_active = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    def save(self) -> None:
        """Save profile to disk (thread-safe)."""
        save_profile(self)
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary."""
        algo_stats = self.preferences.get('algorithms_used', {})
        most_used = max(algo_stats.items(), key=lambda x: x[1]['count']) if algo_stats else ("None", {'count': 0})
        
        return {
            'total_experiments': self.total_experiments,
            'total_sessions': self.total_sessions,
            'total_runtime_hours': self.preferences.get('total_runtime_seconds', 0) / 3600,
            'datasets_processed': self.preferences.get('datasets_processed', 0),
            'unique_algorithms_used': len(algo_stats),
            'most_used_algorithm': most_used[0],
            'most_used_count': most_used[1]['count'],
            'best_accuracy': self.preferences.get('best_accuracy_achieved', 0.0),
            'systems_used': len(set([h['system'] for h in self.preferences.get('system_history', [])])),
        }


def get_user_dir() -> Path:
    """Get the user profiles directory."""
    custom_dir = os.environ.get('MHA_USER_DIR')
    if custom_dir:
        user_dir = Path(custom_dir)
    else:
        user_dir = Path(__file__).parent.parent / 'persistent_state' / 'users'
    
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_session_dir() -> Path:
    """Get the session profiles directory."""
    session_dir = get_user_dir() / 'sessions'
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def generate_user_id(username: str, system_id: str) -> str:
    """Generate unique user ID from username and system."""
    combined = f"{username}@{system_id}"
    return hashlib.md5(combined.encode()).hexdigest()[:16]


def generate_session_id() -> str:
    """Generate unique session ID."""
    return str(uuid.uuid4())


def get_current_user_info() -> tuple:
    """Get current user and system information from environment or system."""
    # Check environment variables first
    username = os.environ.get('MHA_USER')
    system_id = os.environ.get('MHA_SYSTEM')
    session_id = os.environ.get('MHA_SESSION')
    
    # Fallback to system defaults
    if not username:
        try:
            username = getpass.getuser()
        except:
            username = 'user'
    
    if not system_id:
        try:
            system_id = platform.node()
        except:
            system_id = 'unknown'
    
    if not session_id:
        session_id = generate_session_id()
    
    return username, system_id, session_id


def get_profile_path(username: str, system_id: str, session_id: Optional[str] = None) -> Path:
    """Get the file path for a user profile."""
    user_id = generate_user_id(username, system_id)
    
    if session_id:
        # Session-based profile
        return get_session_dir() / f"{user_id}_{session_id}.json"
    else:
        # Persistent profile
        return get_user_dir() / f"{user_id}.json"


def atomic_write(file_path: Path, data: Dict[str, Any]) -> None:
    """
    Atomically write data to file with proper locking.
    Uses temporary file + rename for atomic operation.
    """
    temp_path = file_path.with_suffix('.tmp')
    
    try:
        # Write to temporary file
        with open(temp_path, 'w') as f:
            # Try to lock file (Unix-like systems only)
            if FCNTL_AVAILABLE:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except (AttributeError, OSError):
                    pass
            
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
            
            # Unlock
            if FCNTL_AVAILABLE:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (AttributeError, OSError):
                    pass
        
        # Atomic rename
        if os.name == 'nt':  # Windows
            if file_path.exists():
                os.remove(file_path)
        os.rename(temp_path, file_path)
        
    except Exception as e:
        # Cleanup on error
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except:
                pass
        raise e


def atomic_read(file_path: Path) -> Dict[str, Any]:
    """
    Atomically read data from file with proper locking.
    """
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            with open(file_path, 'r') as f:
                # Try to lock file for reading (Unix-like systems only)
                if FCNTL_AVAILABLE:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    except (AttributeError, OSError):
                        pass
                
                data = json.load(f)
                
                # Unlock
                if FCNTL_AVAILABLE:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except (AttributeError, OSError):
                        pass
                
                return data
                
        except (json.JSONDecodeError, IOError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise e
    
    raise IOError(f"Failed to read {file_path} after {max_retries} attempts")


def create_profile(username: str, system_id: str, session_id: Optional[str] = None) -> UserProfile:
    """
    Create a new user profile.
    
    Args:
        username: User's name
        system_id: System/machine identifier
        session_id: Optional session ID for session-based profiles
    
    Returns:
        UserProfile object
    """
    user_id = generate_user_id(username, system_id)
    if not session_id:
        session_id = generate_session_id()
    
    profile = UserProfile(
        username=username,
        system_id=system_id,
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now().isoformat(),
        last_active=datetime.now().isoformat(),
        is_session_based=session_id is not None
    )
    
    return profile


def create_session_profile(username: str, session_id: Optional[str] = None, 
                          system_id: Optional[str] = None) -> UserProfile:
    """
    Create a session-based profile for concurrent user access.
    This is ideal for web applications with multiple concurrent users.
    
    Args:
        username: User's name
        session_id: Optional unique session ID (generated if not provided)
        system_id: Optional system identifier (auto-detected if not provided)
    
    Returns:
        UserProfile object with session isolation
    """
    if not system_id:
        _, system_id, _ = get_current_user_info()
    
    if not session_id:
        session_id = generate_session_id()
    
    profile = create_profile(username, system_id, session_id)
    profile.is_session_based = True
    
    # Try to load existing persistent profile preferences
    persistent_profile_path = get_profile_path(username, system_id, session_id=None)
    if persistent_profile_path.exists():
        try:
            lock = get_profile_lock(profile.user_id)
            with lock:
                data = atomic_read(persistent_profile_path)
                # Copy preferences from persistent profile
                profile.preferences = data.get('preferences', profile.preferences)
        except:
            pass  # Use defaults if loading fails
    
    # Save session profile
    save_profile(profile)
    
    return profile


def load_profile(username: Optional[str] = None, system_id: Optional[str] = None, 
                session_id: Optional[str] = None) -> UserProfile:
    """
    Load an existing user profile or create a new one.
    Thread-safe with proper locking.
    
    Args:
        username: User's name (auto-detected if None)
        system_id: System identifier (auto-detected if None)
        session_id: Session ID for session-based profiles
    
    Returns:
        UserProfile object
    """
    # Get user info from environment or system
    if not username or not system_id:
        env_user, env_system, env_session = get_current_user_info()
        username = username or env_user
        system_id = system_id or env_system
        if not session_id:
            session_id = env_session
    
    user_id = generate_user_id(username, system_id)
    profile_path = get_profile_path(username, system_id, session_id)
    
    lock = get_profile_lock(user_id)
    
    with lock:
        if profile_path.exists():
            try:
                data = atomic_read(profile_path)
                profile = UserProfile(**data)
                profile.last_active = datetime.now().isoformat()
                
                # Save updated timestamp
                atomic_write(profile_path, profile.to_dict())
                
                return profile
            except Exception as e:
                print(f"Warning: Failed to load profile, creating new one. Error: {e}")
        
        # Create new profile if doesn't exist
        profile = create_profile(username, system_id, session_id)
        atomic_write(profile_path, profile.to_dict())
        
        return profile


def save_profile(profile: UserProfile) -> None:
    """
    Save user profile to disk (thread-safe).
    
    Args:
        profile: UserProfile object to save
    """
    profile.last_active = datetime.now().isoformat()
    profile_path = get_profile_path(profile.username, profile.system_id, 
                                   profile.session_id if profile.is_session_based else None)
    
    lock = get_profile_lock(profile.user_id)
    
    with lock:
        atomic_write(profile_path, profile.to_dict())


def load_session_profile(username: str, system_id: str, session_id: str) -> UserProfile:
    """
    Load a specific session profile.
    
    Args:
        username: User's name
        system_id: System identifier
        session_id: Session ID
    
    Returns:
        UserProfile object
    """
    return load_profile(username, system_id, session_id)


def list_profiles() -> list:
    """
    List all user profiles (both persistent and session-based).
    Returns unique users by username.
    """
    user_dir = get_user_dir()
    session_dir = get_session_dir()
    profiles = []
    seen_users = set()  # Track unique usernames
    
    # Check persistent profiles first (in users directory)
    for profile_file in user_dir.glob('*.json'):
        try:
            data = atomic_read(profile_file)
            username = data.get('username')
            
            if username and username not in seen_users:
                seen_users.add(username)
                profiles.append({
                    'username': username,
                    'system_id': data.get('system_id'),
                    'user_id': data.get('user_id'),
                    'last_active': data.get('last_active'),
                    'total_experiments': data.get('total_experiments', 0),
                    'profile_type': 'persistent'
                })
        except:
            continue
    
    # Check session profiles (in sessions directory) for any new users
    for profile_file in session_dir.glob('*.json'):
        try:
            data = atomic_read(profile_file)
            username = data.get('username')
            
            # Only add if not already in persistent profiles
            if username and username not in seen_users:
                seen_users.add(username)
                profiles.append({
                    'username': username,
                    'system_id': data.get('system_id'),
                    'user_id': data.get('user_id'),
                    'last_active': data.get('last_active'),
                    'total_experiments': data.get('total_experiments', 0),
                    'profile_type': 'session'
                })
        except:
            continue
    
    return profiles


def cleanup_expired_sessions(max_age_hours: int = 24) -> int:
    """
    Clean up expired session profiles.
    
    Args:
        max_age_hours: Maximum age in hours before session is considered expired
    
    Returns:
        Number of sessions cleaned up
    """
    session_dir = get_session_dir()
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    cleaned = 0
    
    for session_file in session_dir.glob('*.json'):
        try:
            # Check file modification time
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            
            if mtime < cutoff_time:
                # Double check by reading the file
                data = atomic_read(session_file)
                last_active = datetime.fromisoformat(data.get('last_active', '2000-01-01'))
                
                if last_active < cutoff_time:
                    session_file.unlink()
                    cleaned += 1
        except:
            continue
    
    return cleaned


def export_profile(profile: UserProfile, output_path: str) -> None:
    """Export profile to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(profile.to_dict(), f, indent=2)


def import_profile(input_path: str) -> UserProfile:
    """Import profile from JSON file."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    profile = UserProfile(**data)
    save_profile(profile)
    
    return profile


def save_session_result(username: str, session_id: str, result_data: Dict[str, Any]) -> None:
    """
    Save optimization result for a specific session.
    
    Parameters
    ----------
    username : str
        Username
    session_id : str
        Session identifier
    result_data : dict
        Result data to save
    """
    profile = load_session_profile(username, platform.node(), session_id)
    profile.increment_experiments()
    save_profile(profile)


def get_session_history(username: str, system_id: Optional[str] = None) -> list:
    """
    Get all session history for a user.
    
    Parameters
    ----------
    username : str
        Username
    system_id : str, optional
        System identifier (defaults to current system)
    
    Returns
    -------
    list
        List of session data
    """
    if system_id is None:
        system_id = platform.node()
    
    session_dir = get_session_dir()
    user_id = generate_user_id(username, system_id)
    
    sessions = []
    for session_file in session_dir.glob(f"{user_id}_*.json"):
        try:
            profile_data = atomic_read(session_file)
            sessions.append(profile_data)
        except:
            continue
    
    return sorted(sessions, key=lambda x: x.get('last_active', ''), reverse=True)


# Backward compatibility aliases
get_current_user = get_current_user_info
switch_profile = load_profile


# Auto-cleanup on module import (non-blocking)
def _auto_cleanup():
    """Auto cleanup expired sessions in background."""
    try:
        cleanup_expired_sessions(max_age_hours=24)
    except:
        pass


# Run cleanup in background
import atexit
atexit.register(_auto_cleanup)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MHA Toolbox User Profile Manager')
    parser.add_argument('--create', metavar='USERNAME', help='Create new user profile')
    parser.add_argument('--system', metavar='SYSTEM_ID', help='System identifier')
    parser.add_argument('--session', metavar='SESSION_ID', help='Session identifier')
    parser.add_argument('--list', action='store_true', help='List all profiles')
    parser.add_argument('--export', metavar='OUTPUT', help='Export profile to file')
    parser.add_argument('--import', dest='import_file', metavar='INPUT', help='Import profile from file')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup expired sessions')
    
    args = parser.parse_args()
    
    if args.list:
        profiles = list_profiles()
        print(f"\nFound {len(profiles)} profiles:\n")
        for p in profiles:
            print(f"  • {p['username']} ({p['system_id']})")
            print(f"    Last active: {p['last_active']}")
            print(f"    Experiments: {p['total_experiments']}\n")
    
    elif args.create:
        system_id = args.system or platform.node()
        session_id = args.session
        
        if session_id:
            profile = create_session_profile(args.create, session_id, system_id)
            print(f"\n✅ Created session profile for {args.create}")
            print(f"   Session ID: {session_id}")
        else:
            profile = create_profile(args.create, system_id)
            save_profile(profile)
            print(f"\n✅ Created profile for {args.create}")
        
        print(f"   System: {system_id}")
        print(f"   User ID: {profile.user_id}\n")
    
    elif args.export:
        username, system_id, _ = get_current_user_info()
        profile = load_profile(username, system_id)
        export_profile(profile, args.export)
        print(f"\n✅ Exported profile to {args.export}\n")
    
    elif args.import_file:
        profile = import_profile(args.import_file)
        print(f"\n✅ Imported profile for {profile.username}\n")
    
    elif args.cleanup:
        cleaned = cleanup_expired_sessions()
        print(f"\n✅ Cleaned up {cleaned} expired sessions\n")
    
    else:
        parser.print_help()
