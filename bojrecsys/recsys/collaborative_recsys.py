import numpy as np
import pandas as pd
import torch

from requests import HTTPError
from scipy.sparse import csr_matrix

from .recsys import RecSys
from ..pipeline import DataDownloader
from .. import utils

class MultiVAE(torch.nn.Module):
    def __init__(self, user_item_matrix: csr_matrix) -> None:
        super(MultiVAE, self).__init__()
        self.user_item_matrix = torch.tensor(user_item_matrix.todense(), dtype=torch.float32)

        self.dropout = torch.nn.Dropout(p=0.5)
        self.encoder_dim = [self.user_item_matrix.shape[1]] + [2000, 300]
        self.decoder_dim = self.encoder_dim[::-1]
        self.decoder_dim[0] = self.decoder_dim[0] // 2

        self.encoder_layers = torch.nn.ModuleList(
            torch.nn.Linear(self.encoder_dim[i], self.encoder_dim[i+1]) for i in range(len(self.encoder_dim) - 1)
        )
        self.decoder_layers = torch.nn.ModuleList(
            torch.nn.Linear(self.decoder_dim[i], self.decoder_dim[i+1]) for i in range(len(self.decoder_dim) - 1)
        )
        
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        input = torch.nn.functional.normalize(input)
        input = self.dropout(input)
        mu, log_var = self.encode(input)
        z = self.reparametrize(mu, log_var)
        recon_input = self.decode(z)
        return recon_input, mu, log_var
    
    def reparametrize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        if self.training:
            std = torch.exp(0.5 * log_var)
            eps = torch.randn_like(std)
            return mu + eps * std
        else:
            return mu
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.encoder_layers[:-1]:
            x = layer(x)
            x = torch.tanh(x)
        x = self.encoder_layers[-1](x)
        mu, log_var = x.chunk(2, dim=1)
        return mu, log_var
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        for layer in self.decoder_layers[:-1]:
            z = layer(z)
            z = torch.tanh(z)
        z = self.decoder_layers[-1](z)
        return z
    
def vae_bce_loss(true: torch.Tensor, pred: torch.Tensor) -> torch.Tensor:
    return -torch.sum(torch.nn.functional.log_softmax(pred, 1) * true, -1)

def vae_reg_loss(mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
    return -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp(), axis=1)

class CollaborativeRecSys(RecSys):

    def __init__(self):
        self.model = None
        self.handle_to_index = {}
        self.problem_id_to_index = {}
        self.index_to_problem_id = {}
        self.user_item_matrix = None

    def fit(self):
        loader = utils.Loader()
        solved_df = loader.load_preproc_df('solved_info')

        handles = list(set(solved_df['handle']))
        for index, handle in enumerate(handles):
            self.handle_to_index[handle] = index
        problem_ids = list(set(solved_df['problemId']))
        for index, problem_id in enumerate(problem_ids):
            self.problem_id_to_index[problem_id] = index
        self.index_to_problem_id = {index: id for id, index in self.problem_id_to_index.items()}
        
        user_item_matrix = np.zeros((len(handles), len(problem_ids)), dtype=np.int32)
        for handle, problem_id in solved_df.itertuples(index=False):
            user_index = self.handle_to_index[handle]
            item_index = self.problem_id_to_index[problem_id]
            user_item_matrix[user_index][item_index] = 1
        self.user_item_matrix = csr_matrix(user_item_matrix)
        self.model = MultiVAE(self.user_item_matrix)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        user_info = torch.tensor(self.user_item_matrix.todense()).to(device)
        dataset = torch.utils.data.TensorDataset(user_info)
        dataloader = torch.utils.data.DataLoader(
            dataset=dataset,
            batch_size=512,
            shuffle=True,
        )
        self.model.to(device)

        for epoch in range(70):
            for (batch_user_info, ) in dataloader:
                optimizer.zero_grad()
                batch_user_info = batch_user_info.to(device).to(torch.float32) 
                recon_users, mu, log_var = self.model(batch_user_info)
                reg_loss = vae_reg_loss(mu, log_var)
                bce_loss = vae_bce_loss(batch_user_info, recon_users)
                loss = (bce_loss + 0.05 * reg_loss).mean()
                loss.backward()
                optimizer.step()
            print(f'epoch: {epoch}')

    def get_recommendations(self, handle: str, problem_num: int) -> list[int]:
        downloader = DataDownloader()
        try:
            problems = downloader.get_top_100_problems(handle)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise KeyError
            else:
                raise e
        
        solved_indices = [self.problem_id_to_index[problem['problemId']] for problem in problems]
        problem_num = len(self.problem_id_to_index)
        solve_info = [1 if index in solved_indices else 0 for index in range(problem_num)]
        solve_info = torch.tensor(solve_info, dtype=torch.float32).unsqueeze(0)
        recon_info, _, _ = self.model(solve_info)
        recon_info = recon_info.squeeze()
        recon_info = torch.where(solve_info == 1, -np.inf, recon_info)
        recommendations = torch.topk(recon_info, problem_num).indices.squeeze().tolist()
        recommendations = [self.index_to_problem_id[index] for index in recommendations]
        return recommendations[:problem_num]

    def get_similar_problems(self, problem_id: int, problem_num: int) -> list[int]:
        return [1001 + i for i in range(problem_num)]