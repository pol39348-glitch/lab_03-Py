import json

import pytest

from toolkit.book import Book
from toolkit.catalog import BookCatalog
from toolkit.errors import (
    BookNotFoundError,
    CorruptedFileError,
    DuplicateBookError,
    InvalidBookError,
    UnsupportedFormatVersionError,
)


def make_book(book_id="b1", title="The Hobbit"):
    return Book(
        book_id=book_id,
        title=title,
        category="Fantasy",
        year=1937,
        author="J. R. R. Tolkien",
        isbn="9780000000001",
    )


def test_book_checks_its_fields():
    with pytest.raises(InvalidBookError):
        Book("", "Title", "Fantasy", 2000, "Author", "123")

    with pytest.raises(InvalidBookError):
        Book("b1", "Title", "Fantasy", 0, "Author", "123")


def test_add_get_remove_and_duplicate():
    catalog = BookCatalog()
    book = make_book()

    catalog.add(book)
    assert catalog.get("b1") == book
    assert "b1" in catalog
    assert len(catalog) == 1

    with pytest.raises(DuplicateBookError):
        catalog.add(book)

    catalog.remove("b1")
    assert len(catalog) == 0

    with pytest.raises(BookNotFoundError):
        catalog.get("b1")

    with pytest.raises(BookNotFoundError):
        catalog.remove("b1")


def test_search_and_iteration_order():
    catalog = BookCatalog()
    first = make_book("b1", "The Hobbit")
    second = make_book("b2", "A Hobbit's Journey")
    catalog.add(first)
    catalog.add(second)

    assert catalog.find_by_category("fantasy") == (first, second)
    assert catalog.find_by_name("HOBBIT") == (first, second)
    assert list(catalog) == [first, second]


def test_json_round_trip(tmp_path):
    file_path = tmp_path / "books.json"
    original = BookCatalog()
    original.add(make_book())
    original.save(str(file_path))

    loaded = BookCatalog()
    loaded.load(str(file_path))

    assert list(loaded) == list(original)


def test_unknown_version_does_not_change_catalog(tmp_path):
    file_path = tmp_path / "books.json"
    file_path.write_text(
        json.dumps({"format_version": 99, "books": []}),
        encoding="utf-8",
    )

    catalog = BookCatalog()
    existing_book = make_book()
    catalog.add(existing_book)

    with pytest.raises(UnsupportedFormatVersionError):
        catalog.load(str(file_path))

    assert list(catalog) == [existing_book]


def test_partial_bad_file_does_not_change_catalog(tmp_path):
    file_path = tmp_path / "books.json"
    good_row = {
        "book_id": "b2",
        "title": "Good book",
        "category": "History",
        "year": 2000,
        "author": "A. Author",
        "isbn": "12345",
    }
    bad_row = {
        "book_id": "b3",
        "title": "",
        "category": "History",
        "year": 2001,
        "author": "B. Author",
        "isbn": "67890",
    }
    document = {"format_version": 1, "books": [good_row, bad_row]}
    file_path.write_text(json.dumps(document), encoding="utf-8")

    catalog = BookCatalog()
    existing_book = make_book()
    catalog.add(existing_book)

    with pytest.raises(CorruptedFileError):
        catalog.load(str(file_path))

    assert list(catalog) == [existing_book]