import threading
import logging
import json

from enum                   import Enum
from typing                 import Dict, Any, List, Optional
from pathlib                import Path
from dataclasses            import dataclass, field, asdict



class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass



class KeybindType(Enum):
    SINGLE       = "single"
    COMBINATION  = "combination"



@dataclass
class ColorConfig:
    tolerance: int                = 5
    scan_size: int                = 80
    disallowed_colors: List[int]  = field(default_factory = lambda: [4563230, 15589197])
    


    def validate(self) -> bool:
        if not 0 <= self.tolerance <= 255:
            raise ConfigError(f"Color tolerance must be between 0-255, got {self.tolerance}")
       
        if not 10 <= self.scan_size <= 500:
            raise ConfigError(f"Scan size must be between 10-500, got {self.scan_size}")
       
        if not all(0 <= color <= 0xFFFFFF for color in self.disallowed_colors):
            raise ConfigError("Disallowed colors must be valid RGB values (0-0xFFFFFF)")
        return True



@dataclass
class KeysConfig:
    pre_fire       : str  = "c"
    wall           : str  = "l"
    build          : str  = "p"
    reload_script  : str  = "ctrl+shift+r"
    debug_color    : str  = "f8"
    add_color      : str  = "f9"
    reload_config  : str  = "f10"
    


    def validate(self) -> bool:
        required_keys = ["pre_fire", "wall", "build", "reload_script", "debug_color", "add_color", "reload_config"]
        
        for key in required_keys:
            if not hasattr(self, key) or not getattr(self, key):
                raise ConfigError(f"Missing required keybind: {key}")
      
        return True
    


    def parse_key_combination(self, key_str: str) -> List[str]:
        """Parse key combinations like 'ctrl+shift+r' into ['ctrl', 'shift', 'r']"""
        return [k.strip().lower() for k in key_str.split('+')]



@dataclass
class PerformanceConfig:
    loop_delay: float = 0.001
    


    def validate(self) -> bool:
        if not 0.0001 <= self.loop_delay <= 1.0:
            raise ConfigError(f"Loop delay must be between 0.0001-1.0, got {self.loop_delay}")
        return True



class XConfig:
    """
    Advanced JSON-based configuration system for the macro utility
    """
    


    DEFAULT_CONFIG = {
        "color"                  : {
            "tolerance"          : 5,
            "scan_size"          : 80,
            "disallowed_colors"  : [4563230, 15589197]
        },
        
        "keys"               : {
            "pre_fire"       : "c",
            "wall"           : "l",
            "build"          : "p",
            "reload_script"  : "ctrl+shift+r",
            "debug_color"    : "f8",
            "add_color"      : "f9",
            "reload_config"  : "f10"
        },
        
        "performance"     : {
            "loop_delay"  : 0.001
        }
    }
    


    def __init__(self, config_path : str = "config.x"):
        self.config_path     = Path(config_path)
        self._lock           = threading.RLock()
        self._color_config         : Optional[ColorConfig]        = None
        self._keys_config          : Optional[KeysConfig]         = None
        self._performance_config   : Optional[PerformanceConfig]  = None
        self._callbacks      = []
        self._last_modified  = 0
        
        # Set up logging
        self.logger = logging.getLogger("XConfig")
       
        if not self.logger.handlers:
            handler    = logging.StreamHandler()
            formatter  = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
           
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    


    def add_change_callback(self, callback):
        """Add a callback function to be called when config changes"""
       
        with self._lock:
            self._callbacks.append(callback)
    


    def _notify_callbacks(self):
        """Notify all registered callbacks of config changes"""
       
        for callback in self._callbacks:
            try:
                callback(self)
            
            except Exception as e:
                self.logger.error(f"Error in config change callback: {e}")
    

    
    def load(self) -> bool:
        """
        Load configuration from .x file
        Returns: True if successful, False otherwise
        """
        
        with self._lock:
            try:
                if not self.config_path.exists():
                    self.logger.warning(f"Config file {self.config_path} not found, creating default")
                    return self.create_default()
                
                # Check if file was modified
                current_mtime = self.config_path.stat().st_mtime
                if current_mtime <= self._last_modified:
                    return True  # No changes
                
                self._last_modified = current_mtime
                
                with open(self.config_path, "r", encoding = "utf-8") as f:
                    raw_config = json.load(f)
                
                # Validate and parse config sections
                self._parse_config(raw_config)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                self._notify_callbacks()
                return True
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in config file: {e}")
                return False
          
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return False
    


    def _parse_config(self, raw_config: Dict[str, Any]):
        """Parse and validate raw config dictionary"""
        # Color config
        color_data          = raw_config.get("color", {})
        self._color_config  = ColorConfig(
            tolerance          = color_data.get("tolerance", 5),
            scan_size          = color_data.get("scan_size", 80),
            disallowed_colors  = color_data.get("disallowed_colors", [4563230, 15589197])
        )
        self._color_config.validate()
        
        # Keys config
        keys_data          = raw_config.get("keys", {})
        self._keys_config  = KeysConfig(
            pre_fire       = keys_data.get("pre_fire", "c"),
            wall           = keys_data.get("wall", "l"),
            build          = keys_data.get("build", "p"),
            reload_script  = keys_data.get("reload_script", "ctrl+shift+r"),
            debug_color    = keys_data.get("debug_color", "f8"),
            add_color      = keys_data.get("add_color", "f9"),
            reload_config  = keys_data.get("reload_config", "f10")
        )
        self._keys_config.validate()
        
        # Performance config
        perf_data                 = raw_config.get("performance", {})
       
        self._performance_config  = PerformanceConfig(
            loop_delay = perf_data.get("loop_delay", 0.001)
        )
        self._performance_config.validate()
    


    def save(self) -> bool:
        """
        Save current configuration to .x file
        Returns: True if successful, False otherwise
        """
     
        with self._lock:
            try:
                config_dict = {
                    "color"        : asdict(self.color),
                    "keys"         : asdict(self.keys),
                    "performance"  : asdict(self.performance)
                }
                
                # Create backup if file exists
                if self.config_path.exists():
                    backup_path = self.config_path.with_suffix(".x.bak")
                    self.config_path.rename(backup_path)
                
                with open(self.config_path, "w", encoding = "utf-8") as f:
                    json.dump(config_dict, f, indent = 4, ensure_ascii = False)
                
                self._last_modified = self.config_path.stat().st_mtime
                self.logger.info(f"Configuration saved to {self.config_path}")
                self._notify_callbacks()
                return True
                
            except Exception as e:
                self.logger.error(f"Error saving config: {e}")
                return False
    


    def create_default(self) -> bool:
        """Create default configuration file"""
        with self._lock:
            try:
                self.config_path.parent.mkdir(parents = True, exist_ok = True)
                
                with open(self.config_path, "w", encoding = "utf-8") as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent = 4, ensure_ascii = False)
                
                self._parse_config(self.DEFAULT_CONFIG)
                self._last_modified = self.config_path.stat().st_mtime
                self.logger.info(f"Default configuration created at {self.config_path}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error creating default config: {e}")
                return False
    


    def update_section(self, section: str, **kwargs) -> bool:
        """
        Update a specific configuration section
        """
     
        with self._lock:
            try:
                if section == "color" and self._color_config:
                    for key, value in kwargs.items():
                        if hasattr(self._color_config, key):
                            setattr(self._color_config, key, value)
                    self._color_config.validate()
                    
                elif section == "keys" and self._keys_config:
                    for key, value in kwargs.items():
                        if hasattr(self._keys_config, key):
                            setattr(self._keys_config, key, value)
                    self._keys_config.validate()
                    
                elif section == "performance" and self._performance_config:
                    for key, value in kwargs.items():
                        if hasattr(self._performance_config, key):
                            setattr(self._performance_config, key, value)
                    self._performance_config.validate()
                
                self.save()
                return True
                
            except Exception as e:
                self.logger.error(f"Error updating {section} config: {e}")
                return False
    


    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration dictionary"""
      
        return {
            "color"        : asdict(self.color),
            "keys"         : asdict(self.keys),
            "performance"  : asdict(self.performance)
        }
    


    def validate_all(self) -> bool:
        """Validate all configuration sections"""
       
        with self._lock:
            try:
                self.color.validate()
                self.keys.validate()
                self.performance.validate()
                return True
           
            except ConfigError as e:
                self.logger.error(f"Configuration validation failed: {e}")
                return False
    


    @property
    def color(self) -> ColorConfig:
        if self._color_config is None:
            self.load()
        return self._color_config
    


    @property
    def keys(self) -> KeysConfig:
        if self._keys_config is None:
            self.load()
        return self._keys_config
    


    @property
    def performance(self) -> PerformanceConfig:
        if self._performance_config is None:
            self.load()
        return self._performance_config
    


    def __repr__(self) -> str:
        return f"XConfig(path={self.config_path}, valid={self.validate_all()})"



# Global config instance
_config_instance: Optional[XConfig] = None



def get_config(config_path: str = "config.x") -> XConfig:
    """Get or create the global configuration instance"""
    global _config_instance
   
    if _config_instance is None:
        _config_instance = XConfig(config_path)
        _config_instance.load()
    return _config_instance