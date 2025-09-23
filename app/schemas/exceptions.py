class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass

class ScraperError(Exception):
    """Raised when there is an error during scraping or processing."""
    pass
