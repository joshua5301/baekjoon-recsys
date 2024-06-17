from bojrecsys import Loader
from bojrecsys import ALSRecSys

loader = Loader()
model: ALSRecSys = loader.load_model('ALS_model')
recommendations = model.get_recommendations('37aster', 10)
print(*recommendations, sep=' ')