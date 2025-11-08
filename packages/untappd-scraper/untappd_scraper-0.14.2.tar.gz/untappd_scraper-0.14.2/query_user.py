"""Get an Untappd user's details."""
import logging
import sys

from untappd_scraper.user import User

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)25s:%(lineno)-4d %(levelname)-8s %(message)s",
)
logging.getLogger("parse").setLevel(logging.WARNING)

for user_id in sys.argv[1:]:
    user = User(user_id)
    print(f"\n{user.name=}")
