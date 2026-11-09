import json

from toolkit.book import Book
from toolkit.errors import (
    BookNotFoundError,
    CorruptedFileError,
    DuplicateBookError,
    InvalidBookError,
    UnsupportedFormatVersionError,
)


class BookCatalog:
    FORMAT_VERSION = 1

    def __init__(self) -> None:
        self._books = {}

    def add(self, book: Book) -> None:
        if not isinstance(book, Book):
            raise InvalidBookError("Only Book objects can be added")

        if book.book_id in self._books:
            raise DuplicateBookError(f"Book ID already exists: {book.book_id}")

        self._books[book.book_id] = book

    def get(self, book_id: str) -> Book:
        try:
            return self._books[book_id]
        except KeyError as error:
            raise BookNotFoundError(f"Book not found: {book_id}") from error

    def remove(self, book_id: str) -> None:
        if book_id not in self._books:
            raise BookNotFoundError(f"Book not found: {book_id}")

        del self._books[book_id]

    def find_by_category(self, category: str) -> tuple:
        found_books = []
        wanted_category = category.casefold()

        for book in self._books.values():
            if book.category.casefold() == wanted_category:
                found_books.append(book)

        return tuple(found_books)

    def find_by_name(self, query: str) -> tuple:
        found_books = []
        wanted_name = query.casefold()

        for book in self._books.values():
            if wanted_name in book.title.casefold():
                found_books.append(book)

        return tuple(found_books)

    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self):
        return iter(self._books.values())

    def __contains__(self, book_id: str) -> bool:
        return book_id in self._books

    def save(self, file_path: str) -> None:
        document = {
            "format_version": self.FORMAT_VERSION,
            "books": [],
        }

        for book in self._books.values():
            book_data = {
                "book_id": book.book_id,
                "title": book.title,
                "category": book.category,
                "year": book.year,
                "author": book.author,
                "isbn": book.isbn,
            }
            document["books"].append(book_data)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(document, file, ensure_ascii=False, indent=2)
        except OSError as error:
            raise CorruptedFileError(f"Could not write file: {file_path}") from error

    def load(self, file_path: str) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                document = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise CorruptedFileError(f"Could not read valid JSON: {file_path}") from error

        if not isinstance(document, dict):
            raise CorruptedFileError("The JSON root must be an object")

        version = document.get("format_version")
        if version != self.FORMAT_VERSION:
            raise UnsupportedFormatVersionError(
                f"Unsupported format version: {version}"
            )

        book_rows = document.get("books")
        if not isinstance(book_rows, list):
            raise CorruptedFileError("The 'books' value must be a list")

        loaded_books = {}

        try:
            for row in book_rows:
                if not isinstance(row, dict):
                    raise CorruptedFileError("Each book must be a JSON object")

                book = Book(
                    book_id=row["book_id"],
                    title=row["title"],
                    category=row["category"],
                    year=row["year"],
                    author=row["author"],
                    isbn=row["isbn"],
                )

                if book.book_id in loaded_books:
                    raise CorruptedFileError(
                        f"Duplicate book ID in file: {book.book_id}"
                    )

                loaded_books[book.book_id] = book
        except (KeyError, TypeError, InvalidBookError) as error:
            raise CorruptedFileError("A book in the file has invalid data") from error

        self._books = loaded_books