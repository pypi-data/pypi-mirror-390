# Untappd Scraper

Web scrape public Untappd pages into data classes.

## Quickstart

### User queries

```python
from untappd_scraper.user import User

users = ["gregavola"]

for user_id in users:
    user = User(user_id)
    print(f"\n{user.name=}")

    for checkin in user.activity():
        print(f"\n\t{checkin.name=}\n\t\t{checkin}")

    print("\n\nLists:")

    for userlist in user.lists():
        print(f"\n\t{userlist.name=} {userlist.num_items=}")

    print("\n\nRecent Venues:")

    for venue in user.venue_history():
        ago = datetime.now().date() - venue.last_visit
        print(
            f"\n\t{venue.name=} {venue.last_visit.strftime('%b %d %Y')} "
            + f"({ago.days} days ago)"
        )```

    print("\n\nRecent Uniques:")

    for beer in user.beer_history():
        print(f"\t{beer}, {beer.total_checkins=}")
```

### Venue queries

```python
from untappd_scraper.venue import Venue

venue_ids = [
    14705,  # 4 pines
    99967,  # collaroy
]

for venue_id in venue_ids:
    venue = Venue(venue_id)
    print(f"\n{venue.name=}")

    for num, checkin in enumerate(venue.activity(), start=1):
        print(f"\n\t{num=}\t{checkin.name=}\n\t\t{checkin}")

# Load a venue by name. Try to be as unambiguous as possible
venue = Venue.from_name("hotel sweeney")
print(f"\n{venue.name=} {venue.verified=}\t{venue.categories=}\n")
print("\n".join([str(beer) for beer in venue.activity()]))

for menu in venue.menus():
    print(f"\n{menu.selection=} / {menu.name=}")

    print("\n\t\t", end="")
    print("\n\t\t".join(str(beer) for beer in menu.beers))
```

## Notes

untappd-scraper is just that - a scraper. It doesn't store data. So, for example,
if you query a user's unique beer history (with `User.beer_history()`) you will not
be able to see the entire history. Just what is public on the web, which is the most
recent 25 uniques.