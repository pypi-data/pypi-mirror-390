import json
import os
import pathlib
import secrets
import uuid
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

# Custom exception for error handling
class TodoziError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

# API Key data model
@dataclass
class ApiKey:
    user_id: str
    public_key: str
    private_key: str
    active: bool = True

    @classmethod
    def new(cls) -> 'ApiKey':
        """Generate a new API key with random values."""
        user_id = str(uuid.uuid4())
        public_key = secrets.token_urlsafe(32)  # 32 bytes for security
        private_key = secrets.token_urlsafe(32)
        return cls(user_id=user_id, public_key=public_key, private_key=private_key, active=True)

    @classmethod
    def with_user_id(cls, user_id: str) -> 'ApiKey':
        """Generate an API key with a specific user ID."""
        public_key = secrets.token_urlsafe(32)
        private_key = secrets.token_urlsafe(32)
        return cls(user_id=user_id, public_key=public_key, private_key=private_key, active=True)

    def matches(self, public_key: str, private_key: Optional[str] = None) -> bool:
        """Check if the public key matches, and optionally the private key."""
        if self.public_key != public_key:
            return False
        if private_key is not None and self.private_key != private_key:
            return False
        return True

    def is_admin(self, public_key: str, private_key: str) -> bool:
        """Check if the key is admin by verifying both keys match."""
        return self.matches(public_key, private_key)

# Collection of API keys with optimized lookups
class ApiKeyCollection:
    def __init__(self):
        self._keys_by_user_id: Dict[str, ApiKey] = {}
        self._keys_by_public: Dict[str, ApiKey] = {}

    def add_key(self, key: ApiKey) -> None:
        """Add a key to the collection."""
        self._keys_by_user_id[key.user_id] = key
        self._keys_by_public[key.public_key] = key

    def get_key(self, user_id: str) -> Optional[ApiKey]:
        """Retrieve a key by user ID."""
        return self._keys_by_user_id.get(user_id)

    def get_key_by_public(self, public_key: str) -> Optional[ApiKey]:
        """Retrieve a key by public key."""
        return self._keys_by_public.get(public_key)

    def get_all_keys(self) -> List[ApiKey]:
        """Get all keys in the collection."""
        return list(self._keys_by_user_id.values())

    def get_active_keys(self) -> List[ApiKey]:
        """Get all active keys."""
        return [key for key in self._keys_by_user_id.values() if key.active]

    def deactivate_key(self, user_id: str) -> bool:
        """Deactivate a key by user ID."""
        if user_id in self._keys_by_user_id:
            self._keys_by_user_id[user_id].active = False
            return True
        return False

    def activate_key(self, user_id: str) -> bool:
        """Activate a key by user ID."""
        if user_id in self._keys_by_user_id:
            self._keys_by_user_id[user_id].active = True
            return True
        return False

    def remove_key(self, user_id: str) -> Optional[ApiKey]:
        """Remove a key by user ID."""
        if user_id in self._keys_by_user_id:
            key = self._keys_by_user_id.pop(user_id)
            self._keys_by_public.pop(key.public_key, None)  # Remove from public key dict
            return key
        return None

# Storage directory management
def get_storage_dir() -> pathlib.Path:
    """Get the storage directory for API keys."""
    home = pathlib.Path.home()
    storage_dir = home / '.todozi'  # Configurable path
    return storage_dir

# Core functions
def save_api_key_collection(collection: ApiKeyCollection) -> None:
    """Save the API key collection to a JSON file."""
    try:
        storage_dir = get_storage_dir()
        api_dir = storage_dir / "api"
        os.makedirs(api_dir, exist_ok=True)
        file_path = api_dir / "api_keys.json"
        
        # Convert collection to JSON-serializable format
        keys_list = [asdict(key) for key in collection.get_all_keys()]
        content = json.dumps(keys_list, indent=4)
        
        with open(file_path, 'w') as f:
            f.write(content)
    except Exception as e:
        raise TodoziError(f"Failed to save API key collection: {str(e)}") from e

def load_api_key_collection() -> ApiKeyCollection:
    """Load the API key collection from a JSON file."""
    try:
        storage_dir = get_storage_dir()
        file_path = storage_dir / "api" / "api_keys.json"
        
        if not file_path.exists():
            return ApiKeyCollection()
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        keys_data = json.loads(content)
        collection = ApiKeyCollection()
        for key_data in keys_data:
            key = ApiKey(**key_data)
            collection.add_key(key)
        
        return collection
    except json.JSONDecodeError as e:
        raise TodoziError(f"Invalid JSON in API key file: {str(e)}") from e
    except Exception as e:
        raise TodoziError(f"Failed to load API key collection: {str(e)}") from e

# API key management functions
def create_api_key() -> ApiKey:
    """Create a new API key."""
    api_key = ApiKey.new()
    collection = load_api_key_collection()
    collection.add_key(api_key)
    save_api_key_collection(collection)
    return api_key

def create_api_key_with_user_id(user_id: str) -> ApiKey:
    """Create a new API key with a specific user ID."""
    api_key = ApiKey.with_user_id(user_id)
    collection = load_api_key_collection()
    collection.add_key(api_key)
    save_api_key_collection(collection)
    return api_key

def get_api_key(user_id: str) -> ApiKey:
    """Get an API key by user ID."""
    collection = load_api_key_collection()
    key = collection.get_key(user_id)
    if key is None:
        raise TodoziError(f"API key not found: {user_id}")
    return key

def get_api_key_by_public(public_key: str) -> ApiKey:
    """Get an API key by public key."""
    collection = load_api_key_collection()
    key = collection.get_key_by_public(public_key)
    if key is None:
        raise TodoziError(f"API key not found for public key: {public_key}")
    return key

def list_api_keys() -> List[ApiKey]:
    """List all API keys."""
    collection = load_api_key_collection()
    return collection.get_all_keys()

def list_active_api_keys() -> List[ApiKey]:
    """List all active API keys."""
    collection = load_api_key_collection()
    return collection.get_active_keys()

def check_api_key_auth(public_key: str, private_key: Optional[str] = None) -> tuple[str, bool]:
    """Check API key authentication and return user ID and admin status."""
    collection = load_api_key_collection()
    key = collection.get_key_by_public(public_key)
    if key is None:
        raise TodoziError("Invalid API key")
    
    if private_key is not None:
        is_admin = key.is_admin(public_key, private_key)
    else:
        is_admin = key.matches(public_key, None)
    return (key.user_id, is_admin)

def deactivate_api_key(user_id: str) -> None:
    """Deactivate an API key by user ID."""
    collection = load_api_key_collection()
    if not collection.deactivate_key(user_id):
        raise TodoziError(f"API key not found: {user_id}")
    save_api_key_collection(collection)

def activate_api_key(user_id: str) -> None:
    """Activate an API key by user ID."""
    collection = load_api_key_collection()
    if not collection.activate_key(user_id):
        raise TodoziError(f"API key not found: {user_id}")
    save_api_key_collection(collection)

def remove_api_key(user_id: str) -> ApiKey:
    """Remove an API key by user ID."""
    collection = load_api_key_collection()
    key = collection.remove_key(user_id)
    if key is None:
        raise TodoziError(f"API key not found: {user_id}")
    save_api_key_collection(collection)
    return key

# API Key Manager class (optional, for future use)
class ApiKeyManager:
    """Manager for API keys (currently not used, but included for completeness)."""
    def __init__(self):
        self.collection = ApiKeyCollection()
