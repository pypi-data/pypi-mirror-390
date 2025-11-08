"""
Portable User Profile Management System
========================================

This module allows users to work with their profiles from anywhere,
including command-line usage, programmatic access, and remote systems.

Usage Examples:

1. Command-Line Usage:
   python -m mha_toolbox.user_profile --user "alice" --system "lab-01"
   python -m mha_toolbox.user_profile --list
   python -m mha_toolbox.user_profile --export profile.json
   python -m mha_toolbox.user_profile --import profile.json

2. Programmatic Usage:
   from mha_toolbox.user_profile import create_profile, load_profile, switch_profile
   
   # Create/load a profile
   profile = create_profile("alice", system_id="lab-01")
   
   # Or load existing
   profile = load_profile("alice", system_id="lab-01")
   
   # Or use environment variables
   import os
   os.environ['MHA_USER'] = 'alice'
   os.environ['MHA_SYSTEM'] = 'lab-01'
   profile = load_profile()  # Auto-loads from env

3. Remote/Cloud Usage:
   # Set environment variables in your remote system
   export MHA_USER="alice"
   export MHA_SYSTEM="cloud-worker-1"
   
   # Your code automatically uses this profile
   from mha_toolbox import optimize
   optimize('pso', dataset, ...)
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import getpass
import platform


@dataclass
class UserProfile:
    """User profile with preferences and settings."""
    username: str
    system_id: str
    user_id: str
    created_at: str
    last_active: str
    total_experiments: int = 0
    total_sessions: int = 0
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                'auto_resume': True,
                'auto_update_best': True,
                'save_worse_results': False,
                'default_algorithms': [],
                'default_iterations': 100,
                'default_population': 30,
                'notification_email': None
            }


def get_user_dir() -> Path:
    """Get the user profiles directory."""
    # Check for custom location from environment
    custom_dir = os.environ.get('MHA_USER_DIR')
    if custom_dir:
        user_dir = Path(custom_dir)
    else:
        # Default location
        user_dir = Path(__file__).parent.parent / 'persistent_state' / 'users'
    
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def generate_user_id(username: str, system_id: str) -> str:
    """Generate unique user ID from username and system."""
    combined = f"{username}@{system_id}"
    return hashlib.md5(combined.encode()).hexdigest()[:16]


def get_current_user_info() -> tuple:
    """Get current user and system information from environment or system."""
    # First check environment variables
    username = os.environ.get('MHA_USER')
    system_id = os.environ.get('MHA_SYSTEM')
    
    # Fall back to system detection
    if not username:
        username = getpass.getuser()
    if not system_id:
        system_id = platform.node()
    
    return username, system_id


def create_profile(username: Optional[str] = None, 
                   system_id: Optional[str] = None,
                   preferences: Optional[Dict] = None) -> UserProfile:
    """
    Create a new user profile.
    
    Args:
        username: Username (default: from env or system)
        system_id: System identifier (default: from env or hostname)
        preferences: User preferences dict
    
    Returns:
        UserProfile object
    
    Examples:
        >>> profile = create_profile("alice", "lab-01")
        >>> profile = create_profile()  # Uses current user/system
    """
    if username is None or system_id is None:
        auto_user, auto_system = get_current_user_info()
        username = username or auto_user
        system_id = system_id or auto_system
    
    user_id = generate_user_id(username, system_id)
    
    profile = UserProfile(
        username=username,
        system_id=system_id,
        user_id=user_id,
        created_at=datetime.now().isoformat(),
        last_active=datetime.now().isoformat(),
        preferences=preferences
    )
    
    # Save profile
    save_profile(profile)
    
    return profile


def load_profile(username: Optional[str] = None,
                 system_id: Optional[str] = None,
                 user_id: Optional[str] = None) -> Optional[UserProfile]:
    """
    Load an existing user profile.
    
    Args:
        username: Username (default: from env or system)
        system_id: System identifier (default: from env or hostname)
        user_id: Direct user ID (if known)
    
    Returns:
        UserProfile object or None if not found
    
    Examples:
        >>> profile = load_profile("alice", "lab-01")
        >>> profile = load_profile()  # Uses current user/system
        >>> profile = load_profile(user_id="abc123def456")
    """
    if user_id is None:
        if username is None or system_id is None:
            auto_user, auto_system = get_current_user_info()
            username = username or auto_user
            system_id = system_id or auto_system
        user_id = generate_user_id(username, system_id)
    
    user_dir = get_user_dir()
    profile_file = user_dir / f"{user_id}.json"
    
    if not profile_file.exists():
        # Create new profile
        return create_profile(username, system_id)
    
    # Load existing profile
    with open(profile_file, 'r') as f:
        data = json.load(f)
    
    # Ensure system_id exists in data (for backward compatibility)
    if 'system_id' not in data:
        data['system_id'] = system_id if system_id else get_current_user_info()[1]
    
    profile = UserProfile(**data)
    
    # Update last active
    profile.last_active = datetime.now().isoformat()
    save_profile(profile)
    
    return profile


def save_profile(profile: UserProfile):
    """Save user profile to disk."""
    user_dir = get_user_dir()
    profile_file = user_dir / f"{profile.user_id}.json"
    
    with open(profile_file, 'w') as f:
        json.dump(asdict(profile), f, indent=2)


def list_profiles() -> list:
    """List all available user profiles."""
    user_dir = get_user_dir()
    profiles = []
    
    for profile_file in user_dir.glob("*.json"):
        with open(profile_file, 'r') as f:
            data = json.load(f)
            # Handle old profiles without system_id
            if 'system_id' not in data:
                data['system_id'] = 'unknown'
            profiles.append({
                'username': data['username'],
                'system_id': data['system_id'],
                'user_id': data['user_id'],
                'last_active': data['last_active'],
                'total_experiments': data.get('total_experiments', 0)
            })
    
    return profiles


def export_profile(profile: UserProfile, export_path: str):
    """
    Export profile to a portable file.
    
    Args:
        profile: UserProfile object
        export_path: Path to export file
    
    Example:
        >>> profile = load_profile()
        >>> export_profile(profile, '/path/to/my_profile.json')
    """
    export_data = asdict(profile)
    export_data['exported_at'] = datetime.now().isoformat()
    export_data['export_version'] = '1.0'
    
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Profile exported to: {export_path}")


def import_profile(import_path: str) -> UserProfile:
    """
    Import profile from a portable file.
    
    Args:
        import_path: Path to import file
    
    Returns:
        UserProfile object
    
    Example:
        >>> profile = import_profile('/path/to/my_profile.json')
    """
    with open(import_path, 'r') as f:
        data = json.load(f)
    
    # Remove export metadata
    data.pop('exported_at', None)
    data.pop('export_version', None)
    
    # Update last active
    data['last_active'] = datetime.now().isoformat()
    
    profile = UserProfile(**data)
    save_profile(profile)
    
    print(f"✅ Profile imported: {profile.username}@{profile.system_id}")
    return profile


def switch_profile(username: str, system_id: str):
    """
    Switch to a different user profile.
    
    Args:
        username: Username
        system_id: System identifier
    
    Example:
        >>> switch_profile("alice", "lab-01")
    """
    # Set environment variables
    os.environ['MHA_USER'] = username
    os.environ['MHA_SYSTEM'] = system_id
    
    # Load/create profile
    profile = load_profile(username, system_id)
    
    print(f"✅ Switched to profile: {profile.username}@{profile.system_id}")
    return profile


def get_active_profile() -> UserProfile:
    """
    Get the currently active user profile.
    
    Returns:
        UserProfile object
    
    Example:
        >>> profile = get_active_profile()
        >>> print(f"Current user: {profile.username}")
    """
    return load_profile()


# CLI Support
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MHA Toolbox User Profile Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current profile
  python -m mha_toolbox.user_profile --show
  
  # Switch to a profile
  python -m mha_toolbox.user_profile --user alice --system lab-01
  
  # List all profiles
  python -m mha_toolbox.user_profile --list
  
  # Export current profile
  python -m mha_toolbox.user_profile --export my_profile.json
  
  # Import a profile
  python -m mha_toolbox.user_profile --import my_profile.json
  
  # Set preferences
  python -m mha_toolbox.user_profile --set-pref auto_resume=true
        """
    )
    
    parser.add_argument('--user', help='Username')
    parser.add_argument('--system', help='System ID')
    parser.add_argument('--show', action='store_true', help='Show current profile')
    parser.add_argument('--list', action='store_true', help='List all profiles')
    parser.add_argument('--export', metavar='FILE', help='Export profile to file')
    parser.add_argument('--import', dest='import_file', metavar='FILE', help='Import profile from file')
    parser.add_argument('--set-pref', metavar='KEY=VALUE', help='Set preference')
    
    args = parser.parse_args()
    
    if args.list:
        profiles = list_profiles()
        print("\n📋 Available Profiles:")
        print("=" * 80)
        for p in profiles:
            print(f"👤 {p['username']}@{p['system_id']}")
            print(f"   User ID: {p['user_id']}")
            print(f"   Experiments: {p['total_experiments']}")
            print(f"   Last active: {p['last_active'][:19]}")
            print()
    
    elif args.import_file:
        profile = import_profile(args.import_file)
        print(f"\n✅ Profile imported and activated!")
        print(f"   Username: {profile.username}")
        print(f"   System: {profile.system_id}")
    
    elif args.user or args.system:
        profile = switch_profile(
            args.user or get_current_user_info()[0],
            args.system or get_current_user_info()[1]
        )
        print(f"\n✅ Profile activated!")
        print(f"   Username: {profile.username}")
        print(f"   System: {profile.system_id}")
        print(f"   User ID: {profile.user_id}")
    
    elif args.export:
        profile = get_active_profile()
        export_profile(profile, args.export)
    
    elif args.set_pref:
        key, value = args.set_pref.split('=')
        profile = get_active_profile()
        
        # Parse value
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        
        profile.preferences[key] = value
        save_profile(profile)
        print(f"✅ Preference set: {key} = {value}")
    
    else:  # Show current profile
        profile = get_active_profile()
        print("\n👤 Current Profile:")
        print("=" * 80)
        print(f"Username: {profile.username}")
        print(f"System: {profile.system_id}")
        print(f"User ID: {profile.user_id}")
        print(f"Total Experiments: {profile.total_experiments}")
        print(f"Total Sessions: {profile.total_sessions}")
        print(f"Last Active: {profile.last_active[:19]}")
        print(f"\n⚙️ Preferences:")
        for key, value in profile.preferences.items():
            print(f"  {key}: {value}")
