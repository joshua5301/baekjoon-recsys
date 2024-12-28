from bojrecsys import *

loader = Loader()
model = CollaborativeRecSys()
model.fit()
recommendations = model.get_recommendations('37aster', 10)
print(*recommendations)