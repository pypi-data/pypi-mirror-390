import importlib
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional
from base.base import BaseCodeParser, BaseConfigParser

@dataclass
class ParserPair:
    code: type[BaseCodeParser]
    config: Optional[type[BaseConfigParser]]

def discover_parsers() -> Dict[str, ParserPair]:
    """
    Discovers parsers by scanning the 'parsers' directory.

    This implementation directly iterates over the file system to avoid
    potential caching issues with pkgutil.
    """
    try:
        import depanalyzer.parsers as root_pkg
    except ImportError:
        # Fallback for direct execution
        import parsers as root_pkg
    
    discovered: Dict[str, ParserPair] = {}
    
    if not hasattr(root_pkg, '__path__') or not root_pkg.__path__:
        return discovered
        
    root_path = Path(root_pkg.__path__[0])
    
    for entry in root_path.iterdir():
        if entry.is_dir() and (entry / "__init__.py").exists():
            lang_pkg_name = entry.name
            full_pkg_name = f"{root_pkg.__name__}.{lang_pkg_name}"
            
            code_cls = None
            config_cls = None

            try:
                mod_code = importlib.import_module(f".code_parser", package=full_pkg_name)
                code_cls = getattr(mod_code, "CodeParser", None)
            except ImportError as e:
                print(f"DEBUG: Caught ImportError for {full_pkg_name}.code_parser: {e}")
                pass
            except Exception as e:
                import traceback
                print(f"DEBUG: Caught generic Exception for {full_pkg_name}.code_parser: {e}")
                traceback.print_exc()

            try:
                mod_cfg = importlib.import_module(f".config_parser", package=full_pkg_name)
                config_cls = getattr(mod_cfg, "ConfigParser", None)
            except ImportError:
                pass
            except Exception as e:
                print(f"DEBUG: Failed to load config_parser for {full_pkg_name}: {e}")

            if code_cls:
                lang_name = getattr(code_cls, "NAME", lang_pkg_name)
                discovered[lang_name] = ParserPair(code=code_cls, config=config_cls)
                
    return discovered
