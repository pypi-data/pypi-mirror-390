"""
Data Serialization Utility for Timber

Provides serialization functions for converting complex data types
(DataFrames, datetime objects, numpy types) into JSON-serializable formats.

This utility is designed to be used across all applications in the Oak ecosystem
that need to serialize data for API responses, Celery tasks, or database storage.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)


def serialize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Serialize a DataFrame to a JSON-compatible format.
    
    Handles:
    - DatetimeIndex → ISO format strings
    - Timestamp objects → ISO format strings  
    - NaN/NA values → None
    - Numpy types → Python native types
    
    Args:
        df: pandas DataFrame to serialize
        
    Returns:
        Dict with serialized data in format:
        {
            'type': 'dataframe',
            'data': [...],  # List of row dicts
            'columns': [...],  # Column names
            'index_name': 'Date',  # If datetime index
            'shape': (rows, cols)
        }
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    try:
        # Handle DatetimeIndex by resetting it to a column
        if isinstance(df.index, pd.DatetimeIndex):
            df_copy = df.reset_index()
            index_name = df.index.name or 'Date'
        else:
            df_copy = df.copy()
            index_name = None
        
        # Convert to dict with records orientation
        data = df_copy.to_dict('records')
        
        # Clean up each record
        for record in data:
            for key, value in list(record.items()):
                # Convert pandas Timestamp to ISO string
                if isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
                # Convert datetime to ISO string
                elif isinstance(value, (datetime, date)):
                    record[key] = value.isoformat()
                # Convert NaN/NA to None
                elif pd.isna(value):
                    record[key] = None
                # Convert numpy types to Python native
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = value.item()
        
        return {
            'type': 'dataframe',
            'data': data,
            'columns': df.columns.tolist(),
            'index_name': index_name,
            'shape': list(df.shape),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
    except Exception as e:
        logger.error(f"Failed to serialize DataFrame: {e}", exc_info=True)
        # Fallback: use pandas JSON serialization
        try:
            return {
                'type': 'dataframe',
                'data': df.to_json(orient='records', date_format='iso'),
                'shape': list(df.shape),
                'serialization': 'json_string',
                'warning': 'Fallback serialization used'
            }
        except Exception as e2:
            # Last resort: string representation
            logger.error(f"Fallback serialization also failed: {e2}")
            return {
                'type': 'dataframe',
                'data': str(df)[:1000],  # Limit size
                'shape': list(df.shape),
                'error': f"Serialization failed: {str(e)}"
            }


def serialize_datetime(dt: Union[datetime, date, time, pd.Timestamp]) -> str:
    """
    Serialize datetime objects to ISO format strings.
    
    Args:
        dt: datetime, date, time, or pandas Timestamp object
        
    Returns:
        ISO format string
    """
    if isinstance(dt, pd.Timestamp):
        return dt.isoformat()
    elif hasattr(dt, 'isoformat'):
        return dt.isoformat()
    else:
        raise TypeError(f"Expected datetime-like object, got {type(dt).__name__}")


def serialize_numpy(value: Union[np.ndarray, np.generic]) -> Union[List, Any]:
    """
    Serialize numpy arrays and scalars to JSON-compatible types.
    
    Args:
        value: numpy array or scalar
        
    Returns:
        Python native list or scalar
    """
    if isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.integer, np.floating)):
        return value.item()
    elif isinstance(value, np.bool_):
        return bool(value)
    else:
        return value


def serialize_value(value: Any) -> Any:
    """
    Recursively serialize any value to JSON-compatible format.
    
    Handles:
    - DataFrames → dict with metadata
    - datetime objects → ISO strings
    - numpy types → Python natives
    - Nested dicts/lists → recursively serialized
    - NaN/NA → None
    
    Args:
        value: Any value to serialize
        
    Returns:
        JSON-serializable version of the value
    """
    # Handle None
    if value is None:
        return None
    
    # Handle NaN/NA
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass  # Not a pandas type
    
    # Handle DataFrame
    if isinstance(value, pd.DataFrame):
        return serialize_dataframe(value)
    
    # Handle pandas Series
    if isinstance(value, pd.Series):
        return serialize_value(value.to_dict())
    
    # Handle datetime types
    if isinstance(value, (pd.Timestamp, datetime, date, time)):
        return serialize_datetime(value)
    
    # Handle numpy types
    if isinstance(value, (np.ndarray, np.generic)):
        return serialize_numpy(value)
    
    # Handle dict - recursively serialize values
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    
    # Handle list/tuple - recursively serialize items
    if isinstance(value, (list, tuple)):
        serialized = [serialize_value(item) for item in value]
        return serialized if isinstance(value, list) else tuple(serialized)
    
    # Handle set
    if isinstance(value, set):
        return [serialize_value(item) for item in value]
    
    # Return as-is for primitive types (str, int, float, bool)
    return value


def deserialize_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Deserialize a DataFrame from the format created by serialize_dataframe.
    
    Args:
        data: Dict with 'type': 'dataframe' and serialized data
        
    Returns:
        Reconstructed pandas DataFrame
    """
    if data.get('type') != 'dataframe':
        raise ValueError("Data is not a serialized DataFrame")
    
    # Handle json_string serialization
    if data.get('serialization') == 'json_string':
        import json
        df = pd.read_json(json.loads(data['data']), orient='records')
        return df
    
    # Standard deserialization
    df = pd.DataFrame(data['data'])
    
    # Restore datetime index if it was present
    if data.get('index_name'):
        index_col = data['index_name']
        if index_col in df.columns:
            df[index_col] = pd.to_datetime(df[index_col])
            df = df.set_index(index_col)
    
    return df


# Convenience function for common use case
def to_json_serializable(obj: Any) -> Any:
    """
    Convert any object to a JSON-serializable format.
    
    This is the main entry point for serialization. Use this function
    when you need to prepare data for JSON encoding.
    
    Args:
        obj: Any object to serialize
        
    Returns:
        JSON-serializable version of the object
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2, 3]})
        >>> serializable = to_json_serializable(df)
        >>> import json
        >>> json.dumps(serializable)  # Works!
    """
    return serialize_value(obj)


# Export main functions
__all__ = [
    'serialize_dataframe',
    'serialize_datetime',
    'serialize_numpy',
    'serialize_value',
    'deserialize_dataframe',
    'to_json_serializable'
]