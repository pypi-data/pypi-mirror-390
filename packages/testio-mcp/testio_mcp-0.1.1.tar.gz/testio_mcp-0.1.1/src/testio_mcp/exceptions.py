"""Custom exceptions for TestIO MCP Server.

This module defines domain exceptions raised by services and converted
to transport-specific formats (MCP error messages, HTTP status codes) by
the tool/controller layer.
"""


class TestIOException(Exception):
    """Base exception for all TestIO MCP errors."""

    pass


class TestNotFoundException(TestIOException):
    """Test not found (404 from TestIO API).

    Raised when:
    - Requested test ID doesn't exist
    - Test has been deleted
    - User doesn't have access to test
    """

    __test__ = False  # Not a pytest test class

    def __init__(self, test_id: int, message: str | None = None):
        """Initialize test not found exception.

        Args:
            test_id: The test ID that wasn't found (integer from API)
            message: Optional custom message
        """
        self.test_id = test_id
        self.message = message or f"Test {test_id} not found"
        super().__init__(self.message)


class TestIOAPIError(TestIOException):
    """TestIO API returned an error (4xx/5xx status code).

    Raised when:
    - Authentication fails (401)
    - Rate limit exceeded (429)
    - Server error (5xx)
    - Other HTTP errors
    """

    __test__ = False  # Not a pytest test class

    def __init__(self, message: str, status_code: int):
        """Initialize API error.

        Args:
            message: Error message (already sanitized by client)
            status_code: HTTP status code from API
        """
        self.message = message
        self.status_code = status_code
        super().__init__(f"API error ({status_code}): {message}")


class ProductNotFoundException(TestIOException):
    """Product not found (404 from TestIO API).

    Raised when:
    - Requested product ID doesn't exist
    - Product has been deleted
    - User doesn't have access to product

    Used in Stories 3-6 for product-related operations.
    """

    __test__ = False  # Not a pytest test class

    def __init__(self, product_id: int, message: str | None = None):
        """Initialize product not found exception.

        Args:
            product_id: The product ID that wasn't found (integer from API)
            message: Optional custom message
        """
        self.product_id = product_id
        self.message = message or f"Product {product_id} not found"
        super().__init__(self.message)


class ValidationError(TestIOException):
    """Input validation error.

    Raised when:
    - Invalid parameters provided
    - Out of range values
    - Invalid continuation tokens
    """

    def __init__(self, field: str, message: str):
        """Initialize validation error.

        Args:
            field: Field name that failed validation
            message: Validation error message
        """
        self.field = field
        self.message = message
        super().__init__(f"Validation error ({field}): {message}")
