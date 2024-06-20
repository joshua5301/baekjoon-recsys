from abc import ABCMeta, abstractmethod

class RecSys(metaclass=ABCMeta):

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def get_recommendations(self, handle: str, problem_num: int):
        pass

    @abstractmethod
    def get_similar_problems(self, problem_id: int, problem_num: int):
        pass
