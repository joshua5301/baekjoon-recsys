from bojrecsys import *

loader = Loader()
model = ItemRecSys()
model.fit()
recommendations = model.get_recommendations('37asterdsedf', 10)
print(*recommendations)