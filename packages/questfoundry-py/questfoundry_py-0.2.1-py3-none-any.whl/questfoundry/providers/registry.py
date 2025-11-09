"""Provider registry for discovering and instantiating providers"""


from .base import ImageProvider, TextProvider
from .config import ProviderConfig


class ProviderRegistry:
    """
    Registry for managing text and image providers.

    The registry handles provider instantiation and configuration,
    allowing easy access to providers by name.

    Example:
        >>> config = ProviderConfig()
        >>> registry = ProviderRegistry(config)
        >>> text_provider = registry.get_text_provider("openai")
        >>> image_provider = registry.get_image_provider("dalle")
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize registry with configuration.

        Args:
            config: Provider configuration
        """
        self.config = config
        self._text_providers: dict[str, type[TextProvider]] = {}
        self._image_providers: dict[str, type[ImageProvider]] = {}
        self._text_instances: dict[str, TextProvider] = {}
        self._image_instances: dict[str, ImageProvider] = {}

        # Register built-in providers
        self._register_builtin_providers()

    def register_text_provider(
        self, name: str, provider_class: type[TextProvider]
    ) -> None:
        """
        Register a text provider class.

        Args:
            name: Provider name (e.g., 'openai', 'ollama')
            provider_class: Provider class to register
        """
        self._text_providers[name] = provider_class

    def register_image_provider(
        self, name: str, provider_class: type[ImageProvider]
    ) -> None:
        """
        Register an image provider class.

        Args:
            name: Provider name (e.g., 'dalle', 'a1111')
            provider_class: Provider class to register
        """
        self._image_providers[name] = provider_class

    def get_text_provider(self, name: str | None = None) -> TextProvider:
        """
        Get or create a text provider instance.

        Args:
            name: Provider name. If None, uses default from config.

        Returns:
            Text provider instance

        Raises:
            ValueError: If provider not found or not registered
        """
        if name is None:
            name = self.config.get_default_provider("text")
            if name is None:
                raise ValueError("No default text provider configured")

        # Return cached instance if available
        if name in self._text_instances:
            return self._text_instances[name]

        # Get provider class
        if name not in self._text_providers:
            raise ValueError(f"Text provider '{name}' not registered")

        provider_class = self._text_providers[name]

        # Get configuration
        try:
            provider_config = self.config.get_provider_config("text", name)
        except KeyError:
            provider_config = {}

        # Create and cache instance
        instance = provider_class(provider_config)
        instance.validate_config()
        self._text_instances[name] = instance

        return instance

    def get_image_provider(self, name: str | None = None) -> ImageProvider:
        """
        Get or create an image provider instance.

        Args:
            name: Provider name. If None, uses default from config.

        Returns:
            Image provider instance

        Raises:
            ValueError: If provider not found or not registered
        """
        if name is None:
            name = self.config.get_default_provider("image")
            if name is None:
                raise ValueError("No default image provider configured")

        # Return cached instance if available
        if name in self._image_instances:
            return self._image_instances[name]

        # Get provider class
        if name not in self._image_providers:
            raise ValueError(f"Image provider '{name}' not registered")

        provider_class = self._image_providers[name]

        # Get configuration
        try:
            provider_config = self.config.get_provider_config("image", name)
        except KeyError:
            provider_config = {}

        # Create and cache instance
        instance = provider_class(provider_config)
        instance.validate_config()
        self._image_instances[name] = instance

        return instance

    def list_text_providers(self) -> list[str]:
        """
        List registered text providers.

        Returns:
            List of text provider names
        """
        return list(self._text_providers.keys())

    def list_image_providers(self) -> list[str]:
        """
        List registered image providers.

        Returns:
            List of image provider names
        """
        return list(self._image_providers.keys())

    def close_all(self) -> None:
        """Close all provider instances and release resources."""
        for text_provider in self._text_instances.values():
            text_provider.close()
        for image_provider in self._image_instances.values():
            image_provider.close()

        self._text_instances.clear()
        self._image_instances.clear()

    def _register_builtin_providers(self) -> None:
        """Register built-in providers."""
        # Import here to avoid circular dependencies and to make
        # provider dependencies optional

        try:
            from .text.openai import OpenAIProvider

            self.register_text_provider("openai", OpenAIProvider)
        except ImportError:
            pass  # OpenAI provider not available

        try:
            from .text.ollama import OllamaProvider

            self.register_text_provider("ollama", OllamaProvider)
        except ImportError:
            pass  # Ollama provider not available

        # Register image providers
        try:
            from .image.dalle import DalleProvider

            self.register_image_provider("dalle", DalleProvider)
        except ImportError:
            pass  # DALL-E provider not available

        try:
            from .image.a1111 import Automatic1111Provider

            self.register_image_provider("a1111", Automatic1111Provider)
        except ImportError:
            pass  # A1111 provider not available
