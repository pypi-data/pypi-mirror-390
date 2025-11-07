from abc import abstractmethod, ABC
from pandas import DataFrame
import logging

class EDA(ABC):
    logger = logging.getLogger(__name__)
    def load_data(self, df: DataFrame):
        self.df = df.copy()

    @abstractmethod
    def standardize_categories(self) -> DataFrame:
        pass

