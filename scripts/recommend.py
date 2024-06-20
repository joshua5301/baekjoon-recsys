from bojrecsys import Loader
from bojrecsys import RecSys

loader = Loader()
model: RecSys = loader.load_model('content_model')
recommendations = model.get_recommendations('37aster', 10)
print(*recommendations)