"""
PgzPlus - Simplified PyGame Zero helper with AI image generation
Install as pgzpro, import as pgzpro
"""

__version__ = "1.0.0"
__author__ = "Georgii Nikishov"

from pgzpro import generator, core, exceptions

center = core.center
cleanup = core.cleanup
actor_generate = generator.actor_generate
bg_generate = generator.bg_generate
no_logging = generator.no_logging
NoInternetError = exceptions.NoInternetError
ImageGenerationError = exceptions.ImageGenerationError
ModelQuotaError = exceptions.ModelQuotaError
APIConnectionError = exceptions.APIConnectionError
ImageProcessingError = exceptions.ImageProcessingError


__all__ = ['center', 'cleanup', 'actor_generate', 'bg_generate', 'no_logging', 'NoInternetError', 'ImageGenerationError', 'ModelQuotaError', 'APIConnectionError', 'ImageProcessingError']