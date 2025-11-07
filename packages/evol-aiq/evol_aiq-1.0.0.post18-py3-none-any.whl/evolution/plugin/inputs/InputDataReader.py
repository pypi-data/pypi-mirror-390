from abc import abstractmethod, ABC
import logging

from pandas import DataFrame


class InputDataReader(ABC):
    logger = logging.getLogger(__name__)
    dataframe = None

    def __init__(self):
        self.dataframe = None

    @abstractmethod
    def load_configs(self, config: dict):
        pass

    @abstractmethod
    def read_data(self):
        pass


    @abstractmethod
    def get_data(self) -> DataFrame:
        pass