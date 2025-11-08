from .php_basics import php_basics
from .php_form import php_form
from .php_db import php_db
from .csharp import csharp
from .asp_state import asp_state
from .asp_validators import asp_validators

def topics():
    return """
WEB DEVELOPMENT PRACTICAL TOPICS ✅

import web1

print(web1.php_basics())
print(web1.php_form())
print(web1.php_db())
print(web1.csharp())
print(web1.asp_state())
print(web1.asp_validators())
"""

__all__ = [
    "topics",
    "php_basics",
    "php_form",
    "php_db",
    "csharp",
    "asp_state",
    "asp_validators"
]
