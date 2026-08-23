"""What the body reads from the environment — and it is one thing.

The pattern is `scripts/tk2/tk2_config.py`'s, proven by the dictionary review: load the body's `.env`
from a path relative to THIS file, before the first `os.getenv`, so the body runs from any working
directory. A daemon started by launchd has no working directory worth the name.

Note what is NOT here: the database name. tk2_config hardcodes its sandbox for a reason — a db name
that comes from the environment is a db name a stray shell export can move, and the thing it could
move onto is the biography. The name is a constant (`tk2.core.constants`) and the guard refuses
everything else. `MONGO_URI` is different in kind: it is an address and a SECRET, it holds no
authority over which database gets opened, and the guard stands between it and any name.
"""

import os

from dotenv import load_dotenv

# The body's `.env` lives in the tk1 package directory — one .env for the whole project, as the
# instruments already assume. From here that is three levels up: tk2/core/ -> tk2/ -> tokeniko-tk2/.
_HERE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "tokeniko", ".env"))

load_dotenv(ENV_PATH)

# NEVER log, print or repr this value: it is a connection string and may carry credentials. It is
# passed to the driver and nowhere else — the datatier's errors name DATABASES, never the URI.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27018/?directConnection=true")

# The driver fails fast rather than hanging a tick: a body that blocks on a dead socket stops
# thinking, which is worse than a body that raises and says why.
SERVER_SELECTION_TIMEOUT_MS = 8000
