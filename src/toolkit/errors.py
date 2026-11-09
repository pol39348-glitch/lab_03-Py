class CatalogError(Exception):
    """Base class for errors raised by the catalog."""


class InvalidBookError(CatalogError):
    """Raised when a book has invalid data."""


class DuplicateBookError(CatalogError):
    """Raised when a book ID is already in the catalog."""


class BookNotFoundError(CatalogError):
    """Raised when a book ID is not in the catalog."""


class UnsupportedFormatVersionError(CatalogError):
    """Raised when a JSON file uses an unknown format version."""


class CorruptedFileError(CatalogError):
    """Raised when a JSON file cannot be loaded as a valid catalog."""