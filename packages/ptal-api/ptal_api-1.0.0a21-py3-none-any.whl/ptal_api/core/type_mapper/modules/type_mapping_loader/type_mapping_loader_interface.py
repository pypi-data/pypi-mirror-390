import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from ptal_api.core.type_mapper.data_model.base_data_model import TypeMapping


class TypeMappingLoaderInterface(ABC):
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @abstractmethod
    def load_type_mapping(self, input_data: Optional[Union[str, dict, TypeMapping]]) -> TypeMapping:
        pass
