from bojrecsys import *

recsys_list: list[RecSys] = [CollaborativeRecSys()]
recsys_names = ['collaborative_recsys']
dumper = Dumper()
for recsys, name in zip(recsys_list, recsys_names):
    recsys.fit()
    dumper.dump_model(recsys, name)

