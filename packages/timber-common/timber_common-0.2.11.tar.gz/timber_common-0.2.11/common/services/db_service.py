"""
Database Service with Connection Retry Logic for Timber Common

Features:
- Automatic retry on connection failures with exponential backoff
- SQLAlchemy session management with context managers
- Connection validation and health checks
- Connection pooling with configurable parameters
- Thread-safe singleton pattern
- CRUD operations for all models (query, count, create, update, delete)
"""

import time
import logging
from typing import Optional, Generator, Any, Dict, List, Type
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text, desc, asc
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, joinedload
from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy.pool import QueuePool

from common.utils.config import config
from common.models import get_model_by_name

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DBService:
    """
    Singleton service for managing SQLAlchemy engine and sessions with retry logic.
    
    Provides both low-level session management and high-level CRUD operations.
    """
    _instance: Optional['DBService'] = None
    _engine = None
    _SessionLocal = None
    _max_retries = 5
    _retry_delay = 2  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBService, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self, max_retries: int = 5, delay: int = 5):
        """
        Initializes the SQLAlchemy engine with connection pooling and retries.
        
        Args:
            max_retries: Maximum number of connection attempts
            delay: Delay between retries in seconds
        """
        db_url = config.get_db_url()
        pool_config = config.get_pool_config()
        
        logger.info(f"Attempting to initialize DB engine to {config.DB_HOST}:{config.DB_PORT}...")

        for attempt in range(max_retries):
            try:
                # Create engine with connection pooling
                self._engine = create_engine(
                    db_url,
                    echo=config.DATABASE_ECHO,
                    poolclass=QueuePool,
                    pool_size=pool_config['pool_size'],
                    max_overflow=pool_config['max_overflow'],
                    pool_timeout=pool_config['pool_timeout'],
                    pool_recycle=pool_config['pool_recycle'],
                    pool_pre_ping=True,  # Verify connections before using
                )
                
                # Set up event listeners for connection management
                @event.listens_for(self._engine, "connect")
                def receive_connect(dbapi_conn, connection_record):
                    """Log new connections."""
                    logger.debug("New database connection established")
                
                @event.listens_for(self._engine, "checkout")
                def receive_checkout(dbapi_conn, connection_record, connection_proxy):
                    """Validate connection on checkout from pool."""
                    logger.debug("Connection checked out from pool")
                
                # Create session factory
                self._SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
                
                # Test the connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                logger.info("DB engine successfully initialized.")
                return
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"DB connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise ConnectionError(
                        "Failed to connect to PostgreSQL after multiple retries."
                    ) from e

    def get_session(self, retry: bool = True) -> Session:
        """
        Creates a new database session with retry logic.
        
        Args:
            retry: Whether to retry on connection failure (default: True)
            
        Returns:
            SQLAlchemy Session object
            
        Raises:
            ConnectionError: If unable to create session after retries
        """
        if not self._SessionLocal:
            raise ConnectionError("Database engine is not initialized.")
        
        attempts = self._max_retries if retry else 1
        
        for attempt in range(attempts):
            try:
                session = self._SessionLocal()
                
                # Validate session with a simple query
                try:
                    session.execute(text("SELECT 1"))
                except Exception as e:
                    logger.error(f"Session validation failed: {e}")
                    session.close()
                    raise
                
                return session
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"Session creation attempt {attempt + 1} failed: {e}")
                
                if attempt < attempts - 1:
                    wait_time = self._retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(
                        f"Failed to create database session after {attempts} attempts"
                    ) from e

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles commits, rollbacks, and session cleanup.
        
        Usage:
            with db_service.session_scope() as session:
                user = User(name="John")
                session.add(user)
                # Auto-commits on exit if no exception
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        params: Optional[dict] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Execute a raw SQL query with automatic session management.
        
        Args:
            query: SQL query string
            params: Query parameters as dictionary
            fetch_one: Return single row
            fetch_all: Return all rows
            
        Returns:
            Query results or None
        """
        with self.session_scope() as session:
            result = session.execute(text(query), params or {})
            
            if fetch_one:
                return result.fetchone()
            elif fetch_all:
                return result.fetchall()
            else:
                return None

    def create_all_tables(self):
        """Create all tables defined in models that inherit from Base."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self._engine)
        logger.info("Database tables created successfully.")

    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self._engine)
        logger.info("All database tables dropped.")

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database health check: OK")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_engine(self):
        """Returns the SQLAlchemy engine (for advanced use cases)."""
        return self._engine

    def close(self):
        """Dispose of the engine and close all connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed and all connections closed.")

    # ========================================================================
    # CRUD Operations (NEW)
    # ========================================================================
    
    def _get_model_class(self, model_name: str) -> Type:
        """
        Get SQLAlchemy model class by name.
        
        Args:
            model_name: Name of the model (e.g., 'UserGoal', 'Notification')
            
        Returns:
            Model class
            
        Raises:
            ValueError: If model not found
        """
        model_class = get_model_by_name(model_name)
        if not model_class:
            raise ValueError(f"Unknown model: {model_name}")
        return model_class
    
    def _apply_filters(self, query, model_class: Type, filters: Dict[str, Any]):
        """Apply filters to query."""
        for field, value in filters.items():
            if value is not None:  # Skip None values
                if hasattr(model_class, field):
                    query = query.filter(getattr(model_class, field) == value)
                else:
                    logger.warning(f"Model {model_class.__name__} has no field '{field}'")
        return query
    
    def _apply_ordering(self, query, model_class: Type, order_by: List[Dict[str, str]]):
        """Apply ordering to query."""
        for order_spec in order_by:
            if isinstance(order_spec, dict):
                for direction, field in order_spec.items():
                    if hasattr(model_class, field):
                        col = getattr(model_class, field)
                        if direction == 'desc':
                            query = query.order_by(desc(col))
                        else:
                            query = query.order_by(asc(col))
                    else:
                        logger.warning(f"Model {model_class.__name__} has no field '{field}'")
        return query
    
    def _load_relationships(self, query, model_class: Type, relationships: List[str]):
        """Eagerly load relationships."""
        for rel_name in relationships:
            if hasattr(model_class, rel_name):
                query = query.options(joinedload(getattr(model_class, rel_name)))
            else:
                logger.warning(f"Model {model_class.__name__} has no relationship '{rel_name}'")
        return query
    
    def _serialize_record(self, record, include_relationships: List[str] = None) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dict."""
        if include_relationships is None:
            include_relationships = []
        
        # Serialize base columns
        result = {
            col.name: getattr(record, col.name)
            for col in record.__table__.columns
        }
        
        # Serialize relationships if loaded
        for rel_name in include_relationships:
            if hasattr(record, rel_name):
                rel_value = getattr(record, rel_name)
                if rel_value is not None:
                    if isinstance(rel_value, list):
                        # One-to-many or many-to-many
                        result[rel_name] = [
                            {col.name: getattr(item, col.name) for col in item.__table__.columns}
                            for item in rel_value
                        ]
                    else:
                        # Many-to-one or one-to-one
                        result[rel_name] = {
                            col.name: getattr(rel_value, col.name)
                            for col in rel_value.__table__.columns
                        }
        
        return result
    
    def query(
        self,
        model: str,
        filters: Optional[Dict[str, Any]] = None,
        include_relationships: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query database records.
        
        Args:
            model: Model name (e.g., 'UserGoal', 'Notification')
            filters: Dict of field: value pairs to filter by
            include_relationships: List of relationship names to eagerly load
            order_by: List of ordering specs [{'desc': 'created_at'}]
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of record dicts
            
        Example:
            results = db_service.query(
                model='UserGoal',
                filters={'user_id': 'abc123', 'status': 'active'},
                include_relationships=['tags'],
                order_by=[{'desc': 'created_at'}],
                limit=50
            )
        """
        if filters is None:
            filters = {}
        if include_relationships is None:
            include_relationships = []
        if order_by is None:
            order_by = []
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Build base query
            query = session.query(model_class)
            
            # Apply filters
            query = self._apply_filters(query, model_class, filters)
            
            # Load relationships
            query = self._load_relationships(query, model_class, include_relationships)
            
            # Apply ordering
            query = self._apply_ordering(query, model_class, order_by)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            # Execute query
            results = query.all()
            
            # Serialize results
            return [
                self._serialize_record(record, include_relationships)
                for record in results
            ]
    
    def count(
        self,
        model: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to filter by
            
        Returns:
            Count of matching records
            
        Example:
            count = db_service.count(
                model='UserGoal',
                filters={'user_id': 'abc123', 'status': 'active'}
            )
        """
        if filters is None:
            filters = {}
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            return query.count()
    
    def create(
        self,
        model: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new database record.
        
        Args:
            model: Model name
            data: Dict of field: value pairs for the new record
            
        Returns:
            Created record as dict
            
        Example:
            new_goal = db_service.create(
                model='UserGoal',
                data={
                    'user_id': 'abc123',
                    'title': 'Learn Python',
                    'status': 'active'
                }
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Create instance
            record = model_class(**data)
            
            # Save to database
            session.add(record)
            session.commit()
            session.refresh(record)
            
            # Serialize and return
            return self._serialize_record(record)
    
    def update(
        self,
        model: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Update database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify records
            data: Dict of field: value pairs to update
            
        Returns:
            Dict with 'updated_count' key
            
        Example:
            result = db_service.update(
                model='UserGoal',
                filters={'id': 'goal-123'},
                data={'status': 'completed'}
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            
            # Perform update
            count = query.update(data)
            session.commit()
            
            return {'updated_count': count}
    
    def delete(
        self,
        model: str,
        filters: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Delete database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify records
            
        Returns:
            Dict with 'deleted_count' key
            
        Example:
            result = db_service.delete(
                model='UserGoal',
                filters={'id': 'goal-123'}
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            
            # Perform delete
            count = query.delete()
            session.commit()
            
            return {'deleted_count': count}
    
    def get_by_id(
        self,
        model: str,
        record_id: str,
        include_relationships: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.
        
        Args:
            model: Model name
            record_id: Primary key value
            include_relationships: List of relationships to load
            
        Returns:
            Record dict or None if not found
            
        Example:
            goal = db_service.get_by_id(
                model='UserGoal',
                record_id='goal-123',
                include_relationships=['tags']
            )
        """
        results = self.query(
            model=model,
            filters={'id': record_id},
            include_relationships=include_relationships,
            limit=1
        )
        return results[0] if results else None


# Create singleton instance
db_service = DBService()


# Helper function for dependency injection (e.g., with FastAPI)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.
    
    Usage with FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = db_service.get_session()
    try:
        yield session
    finally:
        session.close()