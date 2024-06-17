from bojrecsys import Dumper
from bojrecsys import ALSRecSys

als = ALSRecSys()
als.fit()
recommendations = als.get_recommendations('37aster', 10)
print(*recommendations, sep=' ')
dumper = Dumper()
dumper.dump_model(als, 'ALS_model')

