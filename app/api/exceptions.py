"""Custom exceptions for the API"""


class ContractIQException(Exception):
    """Base exception for ContractIQ"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class EmptyUploadError(ContractIQException):
    """Raised when no file is provided in upload"""
    def __init__(self, message: str = "No file provided in upload"):
        super().__init__(message, status_code=400)


class UnsupportedFileTypeError(ContractIQException):
    """Raised when file type is not supported"""
    def __init__(self, message: str = "File type not supported. Only PDF files are allowed."):
        super().__init__(message, status_code=400)


class VectorDBError(ContractIQException):
    """Raised when vector database operations fail"""
    def __init__(self, message: str = "Vector database operation failed"):
        super().__init__(message, status_code=500)


class LLMTimeoutError(ContractIQException):
    """Raised when LLM request times out"""
    def __init__(self, message: str = "LLM request timed out. Please try again."):
        super().__init__(message, status_code=504)


class LLMError(ContractIQException):
    """Raised when LLM returns an error"""
    def __init__(self, message: str = "Error generating response from LLM"):
        super().__init__(message, status_code=500)


class DocumentProcessingError(ContractIQException):
    """Raised when document processing fails"""
    def __init__(self, message: str = "Failed to process document"):
        super().__init__(message, status_code=500)


class NoDocumentsFoundError(ContractIQException):
    """Raised when no documents are found in vector store"""
    def __init__(self, message: str = "No documents found. Please upload a contract first."):
        super().__init__(message, status_code=404)
