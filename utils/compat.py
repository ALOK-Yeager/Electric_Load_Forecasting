"""
Compatibility module for Electric Load Forecasting project

This module provides compatibility functions for different versions of packages,
allowing the code to work with both older and newer versions of libraries.
"""

import logging
import importlib
import inspect
import functools
import warnings

logger = logging.getLogger(__name__)

# BeautifulSoup compatibility
def bs_find_all(soup_element, *args, **kwargs):
    """
    Compatible version of find_all/findAll that works with different BeautifulSoup versions
    
    Args:
        soup_element: BeautifulSoup element or Tag
        *args, **kwargs: Arguments to pass to find_all/findAll
        
    Returns:
        List of found elements
    """
    if soup_element is None:
        return []
        
    try:
        # Try newer BS4 method first
        if hasattr(soup_element, 'find_all'):
            return soup_element.find_all(*args, **kwargs)
        # Fall back to older BS3 method
        elif hasattr(soup_element, 'findAll'):
            return soup_element.findAll(*args, **kwargs)
        else:
            logger.warning(f"Object {type(soup_element)} has neither find_all nor findAll method")
            return []
    except Exception as e:
        logger.error(f"Error in bs_find_all: {str(e)}")
        return []

def bs_find_children(soup_element, *args, **kwargs):
    """
    Compatible version of find_all/findChildren that works with different BeautifulSoup versions
    
    Args:
        soup_element: BeautifulSoup element or Tag
        *args, **kwargs: Arguments to pass to findChildren/find_all
        
    Returns:
        List of found child elements
    """
    if soup_element is None:
        return []
        
    try:
        # Try newer BS4 method first
        if hasattr(soup_element, 'find_all'):
            return soup_element.find_all(*args, **kwargs)
        # Fall back to older BS3 method
        elif hasattr(soup_element, 'findChildren'):
            return soup_element.findChildren(*args, **kwargs)
        else:
            logger.warning(f"Object {type(soup_element)} has neither find_all nor findChildren method")
            return []
    except Exception as e:
        logger.error(f"Error in bs_find_children: {str(e)}")
        return []

# Pandas compatibility
def pd_read_csv_compat(*args, **kwargs):
    """
    Compatible version of pandas.read_csv that works around type checking issues
    
    Args:
        *args, **kwargs: Arguments to pass to pandas.read_csv
        
    Returns:
        DataFrame from pandas.read_csv
    """
    import pandas as pd
    
    # Handle common type errors by converting problematic arguments
    if 'index_col' in kwargs and isinstance(kwargs['index_col'], list):
        # Convert list of strings to single string if only one element
        if len(kwargs['index_col']) == 1:
            kwargs['index_col'] = kwargs['index_col'][0]
    
    # Same for parse_dates
    if 'parse_dates' in kwargs and isinstance(kwargs['parse_dates'], list):
        # Handle single element case
        if len(kwargs['parse_dates']) == 1:
            # Check if we need to convert to a boolean or keep as is
            if kwargs['parse_dates'][0] in [True, False]:
                kwargs['parse_dates'] = kwargs['parse_dates'][0]
    
    try:
        return pd.read_csv(*args, **kwargs)
    except TypeError as e:
        logger.warning(f"Type error in pd.read_csv: {str(e)}, trying alternative approach")
        # Try again with modified arguments
        if 'infer_datetime_format' in kwargs:
            infer_dt = kwargs.pop('infer_datetime_format')
            logger.info(f"Removed infer_datetime_format={infer_dt} from kwargs")
        return pd.read_csv(*args, **kwargs)

# Statsmodels compatibility
def get_statsmodels_version():
    """Get the statsmodels version as a tuple of (major, minor, patch)"""
    try:
        import statsmodels
        version = statsmodels.__version__
        return tuple(map(int, version.split('.')))
    except (ImportError, AttributeError):
        return (0, 0, 0)

def load_arima_model(path):
    """
    Load an ARIMA model in a version-compatible way
    
    Args:
        path (str): Path to the saved model
        
    Returns:
        The loaded model or None if failed
    """
    try:
        version = get_statsmodels_version()
        
        # For newer statsmodels versions
        if version >= (0, 12, 0):
            from statsmodels.tsa.api import SARIMAX
            return SARIMAX.load(path)
        # For older statsmodels versions
        else:
            from statsmodels.tsa.arima_model import ARIMAResults
            try:
                # Older method
                return ARIMAResults.load(path)
            except:
                # Even older method
                import pickle
                with open(path, 'rb') as f:
                    return pickle.load(f)
    except Exception as e:
        logger.error(f"Error loading ARIMA model: {str(e)}")
        return None

def save_arima_model(model, path):
    """
    Save an ARIMA model in a version-compatible way
    
    Args:
        model: The ARIMA/SARIMAX model to save
        path (str): Path to save the model to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Try the direct save method first
        if hasattr(model, 'save'):
            model.save(path)
            return True
            
        # Fall back to pickle
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        return True
    except Exception as e:
        logger.error(f"Error saving ARIMA model: {str(e)}")
        return False
        
def get_model_prediction(model, **kwargs):
    """
    Get predictions from a model in a version-compatible way
    
    Args:
        model: The model to get predictions from
        **kwargs: Arguments to pass to the prediction method
        
    Returns:
        Prediction results or None if failed
    """
    try:
        # Try direct get_prediction method
        if hasattr(model, 'get_prediction'):
            return model.get_prediction(**kwargs)
            
        # Try forecast method
        if hasattr(model, 'forecast'):
            steps = kwargs.get('end', 1) - kwargs.get('start', 0)
            return model.forecast(steps=steps)
            
        # Try predict method
        if hasattr(model, 'predict'):
            return model.predict(**kwargs)
            
        logger.error("No suitable prediction method found")
        return None
    except Exception as e:
        logger.error(f"Error getting model prediction: {str(e)}")
        return None

# TensorFlow/Keras compatibility
def get_tf_version():
    """Get the TensorFlow version as a tuple of (major, minor, patch)"""
    try:
        import tensorflow as tf
        return tuple(map(int, tf.__version__.split('.')))
    except (ImportError, AttributeError):
        return (0, 0, 0)

def set_tf_random_seed(seed):
    """Set TensorFlow random seed in a version-compatible way"""
    try:
        tf_version = get_tf_version()
        import tensorflow as tf
        
        if tf_version >= (2, 0, 0):
            # TF 2.x way
            tf.random.set_seed(seed)
        else:
            # TF 1.x way
            tf.set_random_seed(seed)
    except Exception as e:
        logger.warning(f"Could not set TensorFlow random seed: {str(e)}")

# Django compatibility
def get_django_version():
    """Get the Django version as a tuple of (major, minor, patch)"""
    try:
        import django
        return tuple(map(int, django.__version__.split('.')))
    except (ImportError, AttributeError):
        return (0, 0, 0)