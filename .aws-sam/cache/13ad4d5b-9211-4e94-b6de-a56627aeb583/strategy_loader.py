import yaml
import importlib
import os
import traceback
import sys

def load_strategy(strategy_name):
    """
    Dynamically loads the specified strategy module and function
    """
    logs = []
    try:
        logs.append(f"\nLoading strategy: {strategy_name}")
        
        # Get directories and add to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        strategies_dir = os.path.join(current_dir, 'strategies')
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        if strategies_dir not in sys.path:
            sys.path.insert(0, strategies_dir)
        
        # Load and validate config
        config_path = os.path.join(current_dir, 'strategy_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if strategy_name not in config['strategies']:
            raise ValueError(f"Strategy '{strategy_name}' not found in configuration")
        
        strategy_config = config['strategies'][strategy_name]
        
        # Import strategy module
        try:
            module_name = strategy_config['module'].replace('strategies.', '')
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError(f"Failed to import strategy module '{module_name}': {str(e)}")
        
        # Get strategy function
        function_name = strategy_config['function']
        if not hasattr(module, function_name):
            raise AttributeError(f"Function '{function_name}' not found in module '{module_name}'")
            
        strategy_func = getattr(module, function_name)
        logs.append(f"Strategy loaded successfully")
        
        return strategy_func, strategy_config['params'], logs
        
    except Exception as e:
        logs.append(f"Strategy loading error: {str(e)}")
        logs.append(f"Traceback: {traceback.format_exc()}")
        raise