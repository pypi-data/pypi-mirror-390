class NoInternetError(RuntimeError):
    """Custom exception for no internet connection at start"""
    pass

class ImageGenerationError(RuntimeError):
    """Custom exception for general AI image generation failures"""
    pass

class ModelQuotaError(RuntimeError):
    """Custom exception for model service limitations or temporary unavailability"""
    pass

class APIConnectionError(RuntimeError):
    """Custom exception for API communication issues and connection problems"""
    pass

class ImageProcessingError(RuntimeError):
    """Custom exception for image processing, conversion, or saving failures"""
    pass