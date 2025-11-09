"""
Technical Indicators Module

Handles calculation of technical indicators like moving averages, RSI, Bollinger Bands, etc.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List


def calculate_moving_averages(
    df: pd.DataFrame,
    windows: List[int] = [20, 50, 200],
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates simple moving averages for specified windows.
    
    Args:
        df: DataFrame with price data
        windows: List of window sizes (e.g., [20, 50, 200])
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with MA columns, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        for window in windows:
            df[f'MA_{window}'] = df[price_column].rolling(window=window).mean()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating moving averages: {str(e)}"


def calculate_ema(
    df: pd.DataFrame,
    windows: List[int] = [12, 26],
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates exponential moving averages.
    
    Args:
        df: DataFrame with price data
        windows: List of window sizes
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with EMA columns, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        for window in windows:
            df[f'EMA_{window}'] = df[price_column].ewm(span=window, adjust=False).mean()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating EMA: {str(e)}"


def calculate_rsi(
    df: pd.DataFrame,
    window: int = 14,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Relative Strength Index (RSI).
    
    RSI ranges from 0 to 100:
    - Above 70: Overbought
    - Below 30: Oversold
    
    Args:
        df: DataFrame with price data
        window: Window for RSI calculation (typically 14)
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with RSI column, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        # Calculate price changes
        delta = df[price_column].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate rolling average of gains and losses
        avg_gains = gains.rolling(window=window).mean()
        avg_losses = losses.rolling(window=window).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating RSI: {str(e)}"


def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates MACD (Moving Average Convergence Divergence).
    
    Args:
        df: DataFrame with price data
        fast: Fast EMA window (typically 12)
        slow: Slow EMA window (typically 26)
        signal: Signal line window (typically 9)
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with MACD columns, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        # Calculate EMAs
        ema_fast = df[price_column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[price_column].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        df['MACD'] = ema_fast - ema_slow
        
        # Calculate signal line
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating MACD: {str(e)}"


def calculate_bollinger_bands(
    df: pd.DataFrame,
    window: int = 20,
    num_std: float = 2.0,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Bollinger Bands.
    
    Args:
        df: DataFrame with price data
        window: Window for moving average
        num_std: Number of standard deviations for bands
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with BB columns, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        # Calculate middle band (moving average)
        df['BB_Middle'] = df[price_column].rolling(window=window).mean()
        
        # Calculate standard deviation
        rolling_std = df[price_column].rolling(window=window).std()
        
        # Calculate upper and lower bands
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * num_std)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * num_std)
        
        # Calculate bandwidth
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating Bollinger Bands: {str(e)}"


def calculate_atr(
    df: pd.DataFrame,
    window: int = 14
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Average True Range (ATR) - measure of volatility.
    
    Args:
        df: DataFrame with OHLC data
        window: Window for ATR calculation (typically 14)
        
    Returns:
        Tuple of (DataFrame with ATR column, error message)
    """
    try:
        df = df.copy()
        
        required_cols = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            return df, f"DataFrame must have {required_cols} columns"
        
        # Calculate True Range
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Calculate ATR as rolling average of True Range
        df['ATR'] = true_range.rolling(window=window).mean()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating ATR: {str(e)}"


def calculate_stochastic(
    df: pd.DataFrame,
    k_window: int = 14,
    d_window: int = 3
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Stochastic Oscillator.
    
    Args:
        df: DataFrame with OHLC data
        k_window: Window for %K line (typically 14)
        d_window: Window for %D line (typically 3)
        
    Returns:
        Tuple of (DataFrame with Stochastic columns, error message)
    """
    try:
        df = df.copy()
        
        required_cols = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            return df, f"DataFrame must have {required_cols} columns"
        
        # Calculate %K
        low_min = df['Low'].rolling(window=k_window).min()
        high_max = df['High'].rolling(window=k_window).max()
        
        df['Stochastic_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        
        # Calculate %D (moving average of %K)
        df['Stochastic_D'] = df['Stochastic_K'].rolling(window=d_window).mean()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating Stochastic: {str(e)}"