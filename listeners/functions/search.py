from datetime import datetime
import logging
import urllib
import json
from typing import Optional, Dict, Any

from slack_bolt import Ack, Complete, Fail


class EntityReference:
    """Reference to an external entity"""
    def __init__(self, id: str, type: Optional[str] = None):
        self.id = id
        self.type = type


class SearchResult:
    """Search result returned to Slack"""
    def __init__(self, title: str, description: str, link: str, date_updated: str,
                content: Optional[str], external_ref: EntityReference):
        self.title = title
        self.description = description
        self.link = link
        self.date_updated = date_updated
        self.content = content
        self.external_ref = external_ref
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Slack API"""
        return {
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "date_updated": self.date_updated,
            "content": self.content,
            "external_ref": {"id": self.external_ref.id, "type": self.external_ref.type} if self.external_ref.type else {"id": self.external_ref.id}
        }


class Edition:
    """Represents an edition of a book"""
    def __init__(self, data: Dict[str, Any]):
        self.key = data.get("key", "")
        self.title = data.get("title", "")
        self.publish_date = data.get("publish_date", [])
        self.description = data.get("description", "")


class Book:
    """Represents a book from Open Library API"""
    def __init__(self, data: Dict[str, Any]):
        self.title = data.get("title", "")
        self.key = data.get("key", "")
        self.author_name = data.get("author_name", [])
        self.publish_date = data.get("publish_date", [])
        
        # Parse editions if available
        self.editions = []
        if "editions" in data and "docs" in data["editions"]:
            for edition_data in data["editions"]["docs"]:
                self.editions.append(Edition(edition_data))


class SearchResults:
    """Search results from Open Library API"""
    def __init__(self, data: Dict[str, Any]):
        self.numFound = data.get("numFound", 0)
        self.start = data.get("start", 0)
        self.numFoundExact = data.get("numFoundExact", False)
        self.q = data.get("q", "")
        self.docs = []
        
        # Process and filter docs
        for doc in data.get("docs", [])[:50]:
            # Check required fields
            if "key" not in doc or "title" not in doc:
                continue
                
            # Check editions
            if "editions" not in doc or "docs" not in doc["editions"] or not doc["editions"]["docs"]:
                continue
                
            edition = doc["editions"]["docs"][0]
            if "description" not in edition or not edition.get("publish_date"):
                continue
                
            # Add valid book
            self.docs.append(Book(doc))


def convert_to_iso(date_string: str) -> str:
    """Convert date string to ISO format"""
    formats = [
        "%b %d, %Y",     # "Nov 21, 2002"
        "%B %Y",         # "February 2001"
        "%Y",            # "2021"
        "%Y-%m-%d",      # "1980-01-01"
        "%d %B %Y",      # "20 dezembro 2021"
        "%b %d, %Y",     # "Sep 30, 2001" 
        "%Y/%m/%d",      # "1977/1980"
        "%Y %B",         # "2001 August"
        "%B %d, %Y"      # "January 5, 1998"
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
        # Fetch search results
        search_data = fetch_open_library_search(query)
        
        # Convert to Slack search results
        search_result = []
        for book in search_data.docs:
            edition = book.editions[0]
            
            date_string = edition.publish_date[0] if edition.publish_date else "2000"
            date_updated = convert_to_iso(date_string)
            
            result = SearchResult(
                title=book.title,
                description=edition.description,
                link=f"https://openlibrary.org{book.key}",
                date_updated=date_updated,
                content=edition.description,
                external_ref=EntityReference(id=book.key)
            )
            
            search_result.append(result.to_dict())
            
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
        results = SearchResults(json_data)
        return results
