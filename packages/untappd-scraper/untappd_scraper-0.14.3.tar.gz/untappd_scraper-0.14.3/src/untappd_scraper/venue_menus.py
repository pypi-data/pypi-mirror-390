"""Untappd venue menu functions."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Final

import brotli
from requests_html import HTML, Element, HTMLResponse
from utpd_models_web.beer import WebVenueMenuBeer
from utpd_models_web.constants import UNTAPPD_BASE_URL
from utpd_models_web.menu import WebVenueMenu

from untappd_scraper.html_session import get
from untappd_scraper.web import id_from_href

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection, Iterator, MutableSequence, Sequence


MORE_BEERS_PAGE_SIZE: Final = 15  # XHR more beer page size

# pyright: reportGeneralTypeIssues=false


def venue_menus(resp: HTMLResponse) -> set[WebVenueMenu]:
    """Parse all menus on current page and any other selections.

    Args:
        resp (HTMLResponse): venue's main page

    Returns:
        set[WebVenueMenu]: all venue's menus and their beers
    """
    menus: set[WebVenueMenu] = set()

    for menu_page in menu_pages(resp):
        page_menus = get_menus_on_page(menu_page)
        menus.update(page_menus)

    return menus


def menu_pages(resp: HTMLResponse) -> Iterator[HTMLResponse]:
    """Return all pages containing menus.

    Some venues have a selectable menu pull-down, and each page needs to be loaded
    separately.
    Other venues have all menus on a single page. This will be the already-loaded page
    passed here.
    Non-verified venues have no menu at all

    Args:
        resp (HTMLResponse): loaded venue main page

    Yields:
        Iterator[HTMLResponse]: page(s) containing menu(s)
    """
    menu_header = resp.html.find(".menu-header", first=True)

    if not menu_header:
        return  # pragma: no cover # not verified / no menu

    yield resp  # always want the current page for verified venues

    if menu_selector := menu_header.find(".menu-selector", first=True):  # pyright: ignore[reportAttributeAccessIssue]
        # Now load all the others as required
        current_selection = menu_header.find(".menu-total", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
        selection_values: set[str] = {
            option.attrs["value"]
            for option in menu_selector.find("option")  # pyright: ignore[reportAttributeAccessIssue]
            if option.text != current_selection
        }
        for selection_value in selection_values:
            yield get(resp.url, params={"menu_id": selection_value})  # pyright: ignore[reportCallIssue]


def get_menus_on_page(resp: HTMLResponse) -> set[WebVenueMenu]:
    """Return all found menus on the page.

    Args:
        resp (HTMLResponse): page containing menu(s)

    Returns:
        dict[WebVenueMenu, set[WebVenueMenuBeer]]: menus on page and their beers
    """
    menus: set[WebVenueMenu] = set()

    current_selection = resp.html.find(".menu-select .menu-total", first=True).text  # pyright: ignore[reportAttributeAccessIssue]

    for menu_section in resp.html.find(".menu-section"):
        menu_beers = get_all_menu_items(menu_section)
        venue_menu = menu_details(menu_section, selection=current_selection, beers=menu_beers)
        menus.add(venue_menu)

    return menus


def menu_details(
    menu_section: Element, selection: str, beers: Collection[WebVenueMenuBeer]
) -> WebVenueMenu:
    """Extract info from a menu section and populate a venu menu.

    Args:
        menu_section (Element): single menu section
        selection (str): selected menu page name
        beers (Collection[WebVenueMenuBeer]): beers to assign to this menu

    Returns:
        WebVenueMenu: detail for a single menu
    """
    menu_section_id = menu_section.attrs["id"].partition("_")
    menu_id = int(menu_section_id[-1])
    try:
        menu_name = menu_section.xpath("div/div/h4/text()", first=True).strip()  # pyright: ignore[reportAttributeAccessIssue]
    except AttributeError:  # pragma: no cover
        menu_name = "List"

    try:
        menu_description = menu_section.find(".menu-section-header p", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    except AttributeError:  # pragma: no cover
        menu_description = ""

    return WebVenueMenu(
        menu_id=menu_id,
        name=menu_name,
        description=menu_description,
        selection=selection,
        beers=set(beers),
    )


def get_all_menu_items(menu_section: Element) -> Collection[WebVenueMenuBeer]:
    """Extract beers from a menu.

    Will keep loading "more" until exhausted or no recent updates

    Args:
        menu_section (Element): Menu to extract from

    Returns:
        Collection[MenuItemBeer]: beers on this menu
    """
    menu_beers: MutableSequence[WebVenueMenuBeer] = []

    menu_section_list_el = menu_section.find(".menu-section-list", first=True)
    menu_section_list_items: list[Element] = menu_section_list_el.find("li")  # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

    show_more_section = menu_section.find(".show-more-section", first=True)
    load_more = load_xhr(show_more_section)  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]

    while menu_section_list_items:
        beers = get_menu_items(menu_section_list_items)
        menu_beers.extend(beers)

        if not show_more_section:
            break

        menu_section_list_items = next(load_more, [])  # pragma: no cover

    return tuple(menu_beers)


def load_xhr(
    show_more_section: Element, *, row_size: int = MORE_BEERS_PAGE_SIZE
) -> Iterator[list[Element]]:  # pragma: no cover
    # NOTE don't think they do this any more!
    """Simulate clicking the "show more" button by loading XHR data.

    Args:
        show_more_section (Element): Show More button
        row_size (int, optional): num rows in a menu. Defaults to MORE_BEERS_PAGE_SIZE.

    Yields:
        Iterator[list[Element]]: more beers, a page at a time
    """
    venue_id = show_more_section.attrs["data-venue-id"]
    section_id = show_more_section.attrs["data-section-id"]

    row = 0

    while True:
        row += row_size

        resp = get(
            f"{UNTAPPD_BASE_URL}venue/more_menu/{venue_id}/{row}",
            params={"section_id": section_id},  # pyright: ignore[reportCallIssue]
            headers={  # pyright: ignore[reportCallIssue]
                "Accept-Encoding": "gzip, deflate, br",
                "x-requested-with": "XMLHttpRequest",
            },
        )

        # Sometimes compressed, sometimes not. Sometimes empty :(
        if not resp.content:
            return
        try:
            xhr_json = resp.json()
        except json.JSONDecodeError:
            xhr_content = brotli.decompress(resp.content)
            xhr_json = json.loads(xhr_content)

        if not xhr_json["count"]:
            return

        xhr_html = xhr_json["view"]
        html = HTML(html=xhr_html)
        yield html.find("li")  # newly loaded beers  # pyright: ignore[reportReturnType]


def get_menu_items(menu_section_list_items: list[Element]) -> Sequence[WebVenueMenuBeer]:
    """Extract beers just for this menu section list.

    Args:
        menu_section_list_items (list[Element]): beer items in menu section

    Returns:
        Sequence[WebVenueMenuBeer]: beers in this section
    """
    return tuple(
        beer_detail
        for menu_item in menu_section_list_items
        if (beer_detail := beer_details(menu_item))
    )


def beer_details(menu_item: Element) -> WebVenueMenuBeer | None:
    """Extract beer details from a menu item.

    Args:
        menu_item (Element): single beer element

    Returns:
        WebVenueMenuBeer: interesting details for a beer
    """
    if menu_item.attrs["id"] != "beer":
        return None  # pragma: no cover # some weird spirit menu or something

    beer_el: Element = menu_item.find("h5 > a", first=True)  # pyright: ignore[reportAssignmentType]
    assert beer_el, menu_item

    beer = beer_el.text
    beer_id = id_from_href(beer_el)

    if (img := menu_item.find("div.beer-label img", first=True)) and isinstance(img, Element):
        label = img.attrs["src"]
    else:
        label = ""  # pragma: no cover

    if data_rating_element := menu_item.find("[data-rating]", first=True):
        global_rating: float | None = float(data_rating_element.attrs["data-rating"])  # pyright: ignore[reportAttributeAccessIssue]
    else:
        global_rating = None  # pragma: no cover

    if container := menu_item.find(".beer-containers", first=True):
        serving = container.xpath("div/p/text()")[-1].strip()  # pyright: ignore[reportAttributeAccessIssue, reportIndexIssue]
    else:
        serving = None

    if beer_details := menu_item.find(".beer-details", first=True):
        h6 = beer_details.find("h6", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
        abv, ibu = extract_abv_ibu(h6)
    else:  # pragma: no cover
        abv = None
        ibu = None

    if beer_prices := menu_item.find(".beer-prices", first=True):
        price_tags = beer_prices.find("p")  # pyright: ignore[reportAttributeAccessIssue]
        prices = [
            price_tag.find(".size", first=True).text
            + " "
            + price_tag.find(".price", first=True).text
            for price_tag in price_tags
        ]
    else:
        prices = []

    brewery_el = menu_item.find('[data-href=":brewery"]', first=True)
    brewery_name = brewery_el.text  # pyright: ignore[reportAttributeAccessIssue]
    brewery_id = id_from_href(brewery_el)  # pyright: ignore[reportArgumentType]

    style = str(menu_item.xpath("//h5/em/text()", first=True))

    return WebVenueMenuBeer(
        beer_id=beer_id,
        beer_name=beer,
        beer_label_url=label,
        brewery_id=brewery_id,
        brewery_name=brewery_name,
        brewery_url=None,  # brewery_el.attrs["href"],
        style=style,
        serving=serving,
        prices=prices,
        global_rating=global_rating,
        abv=abv,
        ibu=ibu,
    )


def extract_abv_ibu(abv_ibu: str) -> tuple[float | None, int | None]:
    """Extract ABV and IBU from string in the beer details html.

    Args:
        abv_ibu (str): ABV and IBU string in the beer details html, eg, 10% ABV • N/A IBU

    Returns:
        tuple[float|None, int|None]: ABV and IBU, or None if not found
    """
    if not (match := re.search(r"(?P<abv>.*)% ABV • (?P<ibu>.*) IBU", abv_ibu)):
        return None, None  # pragma: no cover

    abv = match["abv"]
    ibu = match["ibu"]

    try:
        abv = float(abv)
    except ValueError:  # pragma: no cover
        abv = None
    try:
        ibu = int(ibu)
    except ValueError:
        ibu = None

    return abv, ibu
