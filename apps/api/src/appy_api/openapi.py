"""Export the OpenAPI schema without starting the server.

Usage: `python -m appy_api.openapi <output.json>` (see `mise run api:openapi`).
"""

import json
import sys
from pathlib import Path

from appy_api.main import create_app


def main() -> None:
    if len(sys.argv) != 2:  # noqa: PLR2004
        sys.exit("usage: python -m appy_api.openapi <output.json>")
    output = Path(sys.argv[1])
    schema = create_app().openapi()
    output.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
