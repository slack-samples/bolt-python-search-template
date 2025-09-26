import logging
import urllib
import json
from typing import TypedDict, List, Optional, Dict, Union, cast
import concurrent.futures

from slack_bolt import Ack, Complete, Fail


class EntityReference(TypedDict):
    id: str
    type: Optional[str]


class SearchResult(TypedDict):
    title: str
    description: str
    link: str
    date_updated: str
    content: Optional[str]
    external_ref: EntityReference


def handle_search_event(ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger):
    user_context = inputs["user_context"]
    query = inputs["query"]
    filters = inputs["filters"]

    logger.info(f"User {user_context['id']} is executing a search")
    logger.info(f"selected filters: {filters}")

    try:
        search_data = fetch_open_library_search(query)

        search_results: List[SearchResult] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            works = list(executor.map(fetch_open_library_work, [doc["key"] for doc in search_data["docs"]]))
        
        for work in works:
            work['key']
            if not "description" in work:
                continue
            description = work["description"] if isinstance(work["description"], str) else work["description"]["value"]
            search_results.append(
                {
                    "title": work["title"],
                    "description": description,
                    "link": f"https://openlibrary.org/{work['key']}",
                    "date_updated": work["created"]["value"],
                    "content": description,
                    "external_ref": {"id": work['key']},
                }
            )
        complete(outputs={"search_result": search_results})
    except Exception as e:
        logger.exception(e)
        fail(f"Failed to complete the step: {e}")
    finally:
        ack()


class BookDict(TypedDict, total=False):
    """TypedDict representing a book item from Open Library API"""

    title: str
    author_name: List[str]
    cover_i: Optional[int]
    first_publish_year: Optional[int]
    key: str
    edition_count: int
    language: List[str]
    ebook_access: str


class SearchResultsDict(TypedDict, total=False):
    """TypedDict representing search results from Open Library API"""

    numFound: int
    start: int
    numFoundExact: bool
    q: str
    docs: List[BookDict]


class DateTimeValue(TypedDict):
    type: str
    value: str


class AuthorRef(TypedDict):
    key: str


class ExcerptAuthor(TypedDict):
    key: str


class TextValue(TypedDict):
    type: str
    value: str


class WorkDict(TypedDict, total=False):
    """TypedDict representing a work item from Open Library API"""

    description: Optional[Union[TextValue, str]]
    title: str
    covers: List[int]
    subject_places: List[str]
    first_publish_date: str
    subject_people: List[str]
    key: str
    subjects: List[str]
    subject_times: List[str]
    cover_edition: Dict[str, str]
    created: DateTimeValue
    last_modified: DateTimeValue


def fetch_open_library_search(query: str) -> SearchResultsDict:
    url = f"https://openlibrary.org/search.json?q={urllib.parse.quote_plus(query)}"
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        data = response.read()
        json_data = json.loads(data.decode("utf-8"))

        results = cast(SearchResultsDict, json_data)

        if "docs" in results and len(results["docs"]) > 10:
            results["docs"] = results["docs"][:10]

        return results


def fetch_open_library_work(key: str) -> WorkDict:
    url = f"https://openlibrary.org/{key}.json"
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        data = response.read()
        json_data = json.loads(data.decode("utf-8"))

        # Cast to ensure proper typing
        result = cast(WorkDict, json_data)
        return result
