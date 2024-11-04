#!/usr/bin/env sh
# uv export > requirements.txt
python -m zipapp src --compress --output=release/postinstall --python="/usr/bin/env python"
