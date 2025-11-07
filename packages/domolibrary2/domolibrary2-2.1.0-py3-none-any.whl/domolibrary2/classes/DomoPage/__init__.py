"""Page classes and functionality.

This module provides comprehensive page management functionality for Domo pages,
organized into focused submodules:

- exceptions: Page-related exception classes
- core: Main DomoPage entity class with basic operations
- pages: DomoPages collection and hierarchy operations
- access: Access control and sharing functionality
- content: Content management and data operations

Classes:
    DomoPage: Main page entity class
    DomoPages: Collection class for managing multiple pages
    DomoPage_GetRecursive: Exception for recursive operation conflicts
    Page_NoAccess: Exception for page access denial

Example:
    Basic page usage:

        >>> from domolibrary2.classes.DomoPage import DomoPage
        >>> page = await DomoPage.get_by_id(page_id="123", auth=auth)
        >>> print(page.display_url())

    Managing page collections:

        >>> from domolibrary2.classes.DomoPage import DomoPages
        >>> pages = await DomoPages(auth=auth).get()
        >>> print(f"Found {len(pages)} pages")

    Access control:

        >>> access_info = await page.get_accesslist()
        >>> await page.share(domo_users=[user1, user2])
"""

__all__ = [
    "DomoPage_GetRecursive",
    "DomoPage",
    "DomoPages",
    "Page_NoAccess",
    "access",
    "content",
]

# Import and attach functionality modules
from . import access, content

# Import core classes
from .core import DomoPage

# Import exceptions
from .exceptions import DomoPage_GetRecursive, Page_NoAccess
from .pages import DomoPages

# Attach methods to DomoPage class
DomoPage.test_page_access = access.test_page_access
DomoPage.get_accesslist = access.get_accesslist
DomoPage.share = access.share

DomoPage.get_cards = content.get_cards
DomoPage.get_datasets = content.get_datasets
DomoPage.update_layout = content.update_layout
DomoPage.add_owner = content.add_owner
