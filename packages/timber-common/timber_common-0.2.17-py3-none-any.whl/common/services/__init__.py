"""
Business logic services for the Timber Common library.
"""

from .data_fetcher import (
    stock_data_service,
    curated_data_loader,
    StockDataService,
    CuratedDataLoader,
    YFinanceDataFetcher,
    AlphaVantageDataFetcher,
    PolygonDataFetcher,
)

from .db_service import (
    db_service,
    DBService,
    Base,
    get_db,
)

__all__ = [
    # Singleton services (recommended)
    'stock_data_service',
    'curated_data_loader',
    'db_service',
    
    # Service classes
    'StockDataService',
    'CuratedDataLoader',
    'DBService',
    
    # Individual fetchers
    'YFinanceDataFetcher',
    'AlphaVantageDataFetcher',
    'PolygonDataFetcher',
    
    # Database
    'Base',
    'get_db',
]