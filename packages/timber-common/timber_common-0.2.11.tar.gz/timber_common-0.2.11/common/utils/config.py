# timber/common/utils/config.py
"""
Unified Configuration Management for Timber Common Library

This is the SINGLE source of truth for all configuration.
Combines database, API, encryption, vector, and cache settings.

Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()


class Config:
    """
    Singleton class to manage and access environment variables and application settings.
    This centralizes ALL configuration management for Timber Common.
    
    Usage:
        from common.utils.config import config
        
        # Database
        db_url = config.get_db_url()
        
        # API Keys
        av_config = config.get_alpha_vantage_config()
    """
    _instance: Optional['Config'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Loads configuration from environment variables."""
        
        # ===== Environment =====
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.OAK_ENV = os.getenv("OAK_ENV", "development")  # Alias for compatibility
        
        # ===== Database Settings - PostgreSQL =====
        # Primary way: Individual env vars (POSTGRES_*)
        self.DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
        self.DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
        self.DB_USER = os.getenv("POSTGRES_USER", "postgres")
        self.DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        self.DB_NAME = os.getenv("POSTGRES_DB", "timber")
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
        
        # Alternative: Full DATABASE_URL (overrides individual settings if present)
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            # Build from individual components
            self.DATABASE_URL = self.get_db_url()
        
        # Connection Pool Settings
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
        self.DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # ===== Encryption =====
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
        self.MASTER_ENCRYPTION_KEY = os.getenv("MASTER_ENCRYPTION_KEY")
        self.ENCRYPTION_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM", "fernet")
        
        # ===== Vector Database =====
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
        self.VECTOR_INDEX_TYPE = os.getenv("VECTOR_INDEX_TYPE", "ivfflat")
        self.VECTOR_INDEX_LISTS = int(os.getenv("VECTOR_INDEX_LISTS", "100"))
        
        # ===== Cache =====
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        self.CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))
        
        # Redis Cache
        self.REDIS_ENABLED = os.getenv("REDIS_ENABLED", "False").lower() == "true"
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        
        # ===== Logging =====
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # ===== Features =====
        self.ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "False").lower() == "true"
        self.ENABLE_AUTO_VECTOR_INGESTION = os.getenv("ENABLE_AUTO_VECTOR_INGESTION", "False").lower() == "true"
        self.ENABLE_GDPR = os.getenv("ENABLE_GDPR", "True").lower() == "true"
        
        # ===== Performance =====
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
        
        # ===== API Keys - External Data Sources =====
        self.ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.POLYGON_API_KEY: Optional[str] = os.getenv("POLYGON_API_KEY")
        self.FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
        
        # API Base URLs
        self.ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
        self.POLYGON_BASE_URL: str = "https://api.polygon.io"
        self.FINNHUB_BASE_URL: str = "https://finnhub.io/api/v1"
        
        # ===== Data Storage Paths =====
        CURRENT_FILE_DIR = Path(__file__).resolve().parent
        PROJECT_ROOT = CURRENT_FILE_DIR.parents[1]  # From common/utils/config.py to timber/
        self.DATA_DIR: Path = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
        self.MODEL_CONFIG_DIR: Path = Path(os.getenv("MODEL_CONFIG_DIR", PROJECT_ROOT / "config" / "models"))
        self.CURATED_COMPANIES_DIR: Path = self.DATA_DIR / "curated_companies"
        self.CACHE_DIR: Path = self.DATA_DIR / "cache"
        
        # ===== Rate Limiting =====
        self.API_REQUEST_TIMEOUT: int = int(os.getenv("API_REQUEST_TIMEOUT", "20"))
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # ========================================================================
    # Database Methods
    # ========================================================================
    
    def get_db_url(self) -> str:
        """
        Constructs the SQLAlchemy database connection URL.
        
        Returns:
            Database connection string
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_database_config(self) -> bool:
        """
        Validate that database configuration is complete.
        
        Returns:
            True if all required fields are present
        """
        required = [self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]
        return all(required)
    
    def get_pool_config(self) -> Dict[str, int]:
        """
        Returns database connection pool configuration.
        
        Returns:
            Dictionary with pool settings
        """
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
        }
    
    # ========================================================================
    # API Configuration Methods
    # ========================================================================
    
    def get_alpha_vantage_config(self) -> Dict[str, Any]:
        """Returns Alpha Vantage API configuration."""
        return {
            "api_key": self.ALPHA_VANTAGE_API_KEY,
            "base_url": self.ALPHA_VANTAGE_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }

    def get_polygon_config(self) -> Dict[str, Any]:
        """Returns Polygon API configuration."""
        return {
            "api_key": self.POLYGON_API_KEY,
            "base_url": self.POLYGON_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }

    def get_finnhub_config(self) -> Dict[str, Any]:
        """Returns Finnhub API configuration."""
        return {
            "api_key": self.FINNHUB_API_KEY,
            "base_url": self.FINNHUB_BASE_URL,
            "timeout": self.API_REQUEST_TIMEOUT,
        }

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate which API keys are configured.
        
        Returns:
            Dictionary with API key validation status
        """
        return {
            "alpha_vantage": bool(self.ALPHA_VANTAGE_API_KEY and 'use_env' not in str(self.ALPHA_VANTAGE_API_KEY)),
            "polygon": bool(self.POLYGON_API_KEY and 'use_env' not in str(self.POLYGON_API_KEY)),
            "finnhub": bool(self.FINNHUB_API_KEY and 'use_env' not in str(self.FINNHUB_API_KEY)),
        }
    
    # ========================================================================
    # Path Management
    # ========================================================================
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CURATED_COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_model_config_paths(self) -> list:
        """
        Get list of model configuration file paths.
        
        Returns:
            List of Path objects for YAML config files
        """
        if not self.MODEL_CONFIG_DIR.exists():
            return []
        
        return list(self.MODEL_CONFIG_DIR.glob('**/*.yaml'))
    
    # ========================================================================
    # Validation
    # ========================================================================
    
    def validate(self) -> None:
        """
        Validate required configuration.
        
        Raises:
            ValueError: If required configuration is missing
        """
        errors = []
        
        # Check required fields
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL not set and cannot be constructed from individual settings")
        
        if self.ENABLE_ENCRYPTION and not self.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY required when encryption is enabled")
        
        # Validate database URL format
        if self.DATABASE_URL and not self.DATABASE_URL.startswith(('postgresql://', 'sqlite://')):
            errors.append("DATABASE_URL must be PostgreSQL or SQLite")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.OAK_ENV.lower() == 'production' or self.APP_ENV.lower() == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.OAK_ENV.lower() == 'development' or self.APP_ENV.lower() == 'development'
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary (excludes sensitive values)
        """
        return {
            'app_env': self.APP_ENV,
            'oak_env': self.OAK_ENV,
            'database_url': self.DATABASE_URL.split('@')[-1] if '@' in self.DATABASE_URL else self.DATABASE_URL,
            'database_echo': self.DATABASE_ECHO,
            'db_host': self.DB_HOST,
            'db_port': self.DB_PORT,
            'db_name': self.DB_NAME,
            'embedding_model': self.EMBEDDING_MODEL,
            'embedding_dimension': self.EMBEDDING_DIMENSION,
            'cache_enabled': self.CACHE_ENABLED,
            'cache_ttl_hours': self.CACHE_TTL_HOURS,
            'redis_enabled': self.REDIS_ENABLED,
            'enable_encryption': self.ENABLE_ENCRYPTION,
            'enable_auto_vector_ingestion': self.ENABLE_AUTO_VECTOR_INGESTION,
            'enable_gdpr': self.ENABLE_GDPR,
            'log_level': self.LOG_LEVEL,
            'api_keys_configured': self.validate_api_keys()
        }


# Create singleton instance
config = Config()