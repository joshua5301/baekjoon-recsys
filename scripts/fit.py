from bojrecsys import *

recsys_list: list[RecSys] = [LatentFactorRecSys(), ItemRecSys(), ContentRecSys()]
recsys_names = ['latent_factor_model', 'item_model', 'content_model']
dumper = Dumper()
for recsys, name in zip(recsys_list, recsys_names):
    recsys.fit()
    dumper.dump_model(recsys, name)

