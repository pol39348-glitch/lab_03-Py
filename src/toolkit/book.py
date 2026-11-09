from dataclasses import dataclass

from toolkit.errors import InvalidBookError


@dataclass(frozen=True)
class Book:
    book_id: str
    title: str
    category: str
    year: int
    author: str
    isbn: str

    def __post_init__(self) -> None:
        text_fields = [
            ("book_id", self.book_id),
            ("title", self.title),
            ("category", self.category),
            ("author", self.author),
            ("isbn", self.isbn),
        ]

        for field_name, value in text_fields:
            if not isinstance(value, str) or not value.strip():
                raise InvalidBookError(f"{field_name} must be a non-empty string")

        if isinstance(self.year, bool) or not isinstance(self.year, int):
            raise InvalidBookError("year must be an integer")

        if self.year < -9999 or self.year > 9999:
            raise InvalidBookError("year must be between -9999 and 9999")