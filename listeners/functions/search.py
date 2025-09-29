from dataclasses import dataclass, field
from datetime import datetime
import logging
import urllib
import json
from typing import List, Optional, Dict, Any, TypedDict, cast

from slack_bolt import Ack, Complete, Fail

class EntityReference(TypedDict):
    id: str
    type: Optional[str]


class SearchResult(TypedDict):
    title: str
    description: str
    link: str
    date_updated: str
    external_ref: EntityReference

@dataclass
class EditionDoc:
    key: str
    title: str
    publish_date: str
    description: str

@dataclass
class Edition:
    doc: EditionDoc

@dataclass
class Book:
    title: str
    key: str
    author_name: str
    editions: Edition


class SearchResults(TypedDict):
    """Search results from Open Library API"""
    numFound: int
    start: int 
    numFoundExact: bool
    q: str
    docs: List[Dict[str, Any]]

class BooksBuilder:
    _books: List[Book] = []

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._books = []
    
    @property
    def books(self) -> List[Book]:
        return self._books

    def add_book(self, doc: Dict[str, Any]) -> None:
        required_fields = ["key", "title", "editions", "author_name"]
        if any(field not in doc for field in required_fields):
            return
        author_name = self._extract_author_name(doc)
        if author_name is None:
            return
        
        if "docs" not in doc["editions"] or len(doc["editions"]["docs"]) < 1:
            return

        edition_doc = self._extract_edition_doc(doc["editions"]["docs"][0])
        if edition_doc is None:
            return

        self._books.append(
            Book(key=doc["key"], title=doc["title"], author_name=author_name, editions=Edition(doc=edition_doc))
        )

    def _extract_author_name(self, data: Dict[str, Any]) -> Optional[str]:
        if len(data.get("author_name", [])) < 1:
            return None
        return data["author_name"][0]
    
    def _extract_edition_doc(self, data: Dict[str, Any]) -> Optional[EditionDoc]:
        edition_doc_fields = ["key", "title", "publish_date", "description"]
        if any(field not in data for field in edition_doc_fields):
            return None
        print(data["publish_date"])
        if len(data["publish_date"]) < 1:
            return None
        return EditionDoc(key=data["key"], title=data["title"], publish_date=data["publish_date"][0], description=data["description"])


def convert_to_iso(date_string: str) -> str:
    """Convert date string to ISO format"""
    print(date_string)
    formats = [
        "%b %d, %Y",  # "Nov 21, 2002"
        "%B %Y",  # "February 2001"
        "%Y",  # "2021"
        "%Y-%m-%d",  # "1980-01-01"
        "%d %B %Y",  # "20 dezembro 2021"
        "%b %d, %Y",  # "Sep 30, 2001"
        "%Y/%m/%d",  # "1977/1980"
        "%Y %B",  # "2001 August"
        "%B %d, %Y",  # "January 5, 1998"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return "2023-01-01"  # Default if no format works


def handle_search_event(ack: Ack, inputs: dict, fail: Fail, complete: Complete, logger: logging.Logger):
    user_context = inputs["user_context"]
    query = inputs["query"]
    filters = inputs["filters"]

    logger.info(f"User {user_context['id']} is executing a search")
    logger.info(f"selected filters: {filters}")

    try:
        search_data = fetch_open_library_search(query)

        books_builder = BooksBuilder()
        for doc in search_data.get("docs", [])[:50]:
            books_builder.add_book(doc)
        
        books = books_builder.books

        search_result: List[SearchResult] = []
        for book in books:
            result : SearchResult= {
                "title":book.title,
                "description":book.editions.doc.description,
                "link":f"https://openlibrary.org{book.key}",
                "date_updated":convert_to_iso(book.editions.doc.publish_date),
                "content":book.editions.doc.description,
                "external_ref":{"id": book.key}
            }
            search_result.append(result)

        logger.info(f"Found {len(search_result)} search results")
        complete(outputs={"search_result": search_result})
    except Exception as e:
        logger.exception(e)
        fail(f"Failed to complete the step: {e}")
    finally:
        ack()


def fetch_open_library_search(query: str) -> SearchResults:
    """Fetch search results from Open Library API"""
    url = f"https://openlibrary.org/search.json?q={urllib.parse.quote_plus(query)}&fields=key,title,author_name,editions,description,publish_date"
    req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        data = response.read()
        json_data = json.loads(data.decode("utf-8"))

        # Convert JSON to SearchResults object
        results = cast(SearchResults, json_data)
        return results
