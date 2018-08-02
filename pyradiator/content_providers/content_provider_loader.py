import logging
from importlib import import_module


LOGGER = logging.getLogger(__name__)


def load_content_provider(content_provider_name):
    module_name = content_provider_name_to_module_name(content_provider_name)
    module = import_module(module_name)
    class_name = content_provider_name_to_class_name(content_provider_name)
    content_provider = getattr(module, class_name)
    LOGGER.debug("Content provider %s loaded", class_name)
    return content_provider


def content_provider_name_to_module_name(content_provider_name):
    return "pyradiator.content_providers.{}".format(content_provider_name)


def content_provider_name_to_class_name(content_provider_name):
    return content_provider_name.title().replace("_", "")
