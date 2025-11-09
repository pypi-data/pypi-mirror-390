from .auto_model import auto_train
#from .preprocessing import handle_missing, encode_categorical, scale_features, split_data
from .metrics import classification_metrics, regression_metrics

__all__ = [
    'auto_train',
    'handle_missing',
    'encode_categorical',
    'scale_features',
    'split_data',
    'classification_metrics',
    'regression_metrics'
]
