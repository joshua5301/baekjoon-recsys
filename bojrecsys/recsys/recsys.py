from abc import ABCMeta, abstractmethod

class RecSys(metaclass=ABCMeta):

    @abstractmethod
    def fit():
        pass

    @abstractmethod
    def get_recommendations(user: str, item_num: int):
        pass
