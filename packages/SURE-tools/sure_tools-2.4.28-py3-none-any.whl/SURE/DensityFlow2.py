import pyro
import pyro.distributions as dist
from pyro.optim import ExponentialLR
from pyro.infer import SVI, JitTraceEnum_ELBO, TraceEnum_ELBO, config_enumerate

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.distributions.utils import logits_to_probs, probs_to_logits, clamp_probs
from torch.distributions import constraints
from torch.distributions.transforms import SoftmaxTransform

from .utils.custom_mlp import MLP, Exp, ZeroBiasMLP
from .utils.utils import CustomDataset, CustomDataset2, CustomDataset4, tensor_to_numpy, convert_to_tensor


import os
import argparse
import random
import numpy as np
import datatable as dt
from tqdm import tqdm
from scipy import sparse

import scanpy as sc
from .atac import binarize

from typing import Literal

import warnings
warnings.filterwarnings("ignore")

import dill as pickle
import gzip
from packaging.version import Version
torch_version = torch.__version__


def set_random_seed(seed):
    # Set seed for PyTorch
    torch.manual_seed(seed)
    
    # If using CUDA, set the seed for CUDA
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # For multi-GPU setups.
    
    # Set seed for NumPy
    np.random.seed(seed)
    
    # Set seed for Python's random module
    random.seed(seed)

    # Set seed for Pyro
    pyro.set_rng_seed(seed)

class DensityFlow2(nn.Module):
    def __init__(self,
                 input_size: int,
                 codebook_size: int = 200,
                 cell_factor_size: int = 0,
                 turn_off_cell_specific: bool = False,
                 supervised_mode: bool = False,
                 z_dim: int = 10,
                 z_dist: Literal['normal','studentt','laplacian','cauchy','gumbel'] = 'gumbel',
                 loss_func: Literal['negbinomial','poisson','multinomial','bernoulli'] = 'multinomial',
                 inverse_dispersion: float = 10.0,
                 use_zeroinflate: bool = False,
                 hidden_layers: list = [500],
                 hidden_layer_activation: Literal['relu','softplus','leakyrelu','linear'] = 'relu',
                 nn_dropout: float = 0.1,
                 post_layer_fct: list = ['layernorm'],
                 post_act_fct: list = None,
                 config_enum: str = 'parallel',
                 use_cuda: bool = True,
                 seed: int = 42,
                 zero_bias: bool|list = True,
                 dtype = torch.float32, # type: ignore
                 ):
        super().__init__()

        self.input_size = input_size
        self.cell_factor_size = cell_factor_size
        self.inverse_dispersion = inverse_dispersion
        self.latent_dim = z_dim
        self.hidden_layers = hidden_layers
        self.decoder_hidden_layers = hidden_layers[::-1]
        self.allow_broadcast = config_enum == 'parallel'
        self.use_cuda = use_cuda
        self.loss_func = loss_func
        self.options = None
        self.code_size=codebook_size
        self.supervised_mode=supervised_mode
        self.latent_dist = z_dist
        self.dtype = dtype
        self.use_zeroinflate=use_zeroinflate
        self.nn_dropout = nn_dropout
        self.post_layer_fct = post_layer_fct
        self.post_act_fct = post_act_fct
        self.hidden_layer_activation = hidden_layer_activation
        if type(zero_bias) == list:
            self.use_bias = [not x for x in zero_bias]
        else:
            self.use_bias = [not zero_bias] * self.cell_factor_size
        #self.use_bias = not zero_bias
        self.turn_off_cell_specific = turn_off_cell_specific
        
        self.codebook_weights = None

        set_random_seed(seed)
        self.setup_networks()
        
        print(f"🧬 DensityFlow2 Initialized:")
        print(f"   - Latent Dimension: {self.latent_dim}")
        print(f"   - Gene Dimension: {self.input_size}")
        print(f"   - Hidden Dimensions: {self.hidden_layers}")
        print(f"   - Device: {self.get_device()}")
        print(f"   - Parameters: {sum(p.numel() for p in self.parameters()):,}")

    def setup_networks(self):
        latent_dim = self.latent_dim
        hidden_sizes = self.hidden_layers

        nn_layer_norm, nn_batch_norm, nn_layer_dropout = False, False, False
        na_layer_norm, na_batch_norm, na_layer_dropout = False, False, False

        if self.post_layer_fct is not None:
            nn_layer_norm=True if ('layernorm' in self.post_layer_fct) or ('layer_norm' in self.post_layer_fct) else False
            nn_batch_norm=True if ('batchnorm' in self.post_layer_fct) or ('batch_norm' in self.post_layer_fct) else False
            nn_layer_dropout=True if 'dropout' in self.post_layer_fct else False

        if self.post_act_fct is not None:
            na_layer_norm=True if ('layernorm' in self.post_act_fct) or ('layer_norm' in self.post_act_fct) else False
            na_batch_norm=True if ('batchnorm' in self.post_act_fct) or ('batch_norm' in self.post_act_fct) else False
            na_layer_dropout=True if 'dropout' in self.post_act_fct else False

        if nn_layer_norm and nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif nn_layer_norm and nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_layer_fct = lambda layer_ix, total_layers, layer: None

        if na_layer_norm and na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif na_layer_norm and na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_act_fct = lambda layer_ix, total_layers, layer: None

        if self.hidden_layer_activation == 'relu':
            activate_fct = nn.ReLU
        elif self.hidden_layer_activation == 'softplus':
            activate_fct = nn.Softplus
        elif self.hidden_layer_activation == 'leakyrelu':
            activate_fct = nn.LeakyReLU
        elif self.hidden_layer_activation == 'linear':
            activate_fct = nn.Identity

        if self.supervised_mode:
            self.encoder_n = MLP(
                [self.input_size] + hidden_sizes + [self.code_size],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.encoder_n = MLP(
                [self.latent_dim] + hidden_sizes + [self.code_size],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        self.encoder_zn = MLP(
            [self.input_size] + hidden_sizes + [[latent_dim, latent_dim]],
            activation=activate_fct,
            output_activation=[None, Exp],
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )
        
        if self.loss_func == 'negbinomial':
            self.encoder_inverse_dispersion = MLP(
                [self.latent_dim] + hidden_sizes + [[self.input_size, self.input_size]],
                activation=activate_fct,
                output_activation=[Exp, Exp],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        
        if self.cell_factor_size>0:
            self.cell_factor_effect = nn.ModuleList()
            for i in np.arange(self.cell_factor_size):
                if self.use_bias[i]:
                    if self.turn_off_cell_specific:
                        self.cell_factor_effect.append(MLP(
                            [1] + self.decoder_hidden_layers + [self.latent_dim],
                            activation=activate_fct,
                            output_activation=None,
                            post_layer_fct=post_layer_fct,
                            post_act_fct=post_act_fct,
                            allow_broadcast=self.allow_broadcast,
                            use_cuda=self.use_cuda,
                            )
                        )
                    else:
                        self.cell_factor_effect.append(MLP(
                            [self.latent_dim+1] + self.decoder_hidden_layers + [self.latent_dim],
                            activation=activate_fct,
                            output_activation=None,
                            post_layer_fct=post_layer_fct,
                            post_act_fct=post_act_fct,
                            allow_broadcast=self.allow_broadcast,
                            use_cuda=self.use_cuda,
                            )
                        )
                else:
                    if self.turn_off_cell_specific:
                        self.cell_factor_effect.append(ZeroBiasMLP(
                            [1] + self.decoder_hidden_layers + [self.latent_dim],
                            activation=activate_fct,
                            output_activation=None,
                            post_layer_fct=post_layer_fct,
                            post_act_fct=post_act_fct,
                            allow_broadcast=self.allow_broadcast,
                            use_cuda=self.use_cuda,
                            )
                        )
                    else:
                        self.cell_factor_effect.append(ZeroBiasMLP(
                            [self.latent_dim+1] + self.decoder_hidden_layers + [self.latent_dim],
                            activation=activate_fct,
                            output_activation=None,
                            post_layer_fct=post_layer_fct,
                            post_act_fct=post_act_fct,
                            allow_broadcast=self.allow_broadcast,
                            use_cuda=self.use_cuda,
                            )
                        )
            
        self.decoder_concentrate = MLP(
                    [self.latent_dim] + self.decoder_hidden_layers + [self.input_size],
                    activation=activate_fct,
                    output_activation=None,
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )

        if self.latent_dist == 'studentt':
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [[latent_dim,latent_dim]],
                activation=activate_fct,
                output_activation=[Exp,None],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [latent_dim],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        if self.use_cuda:
            self.cuda()

    def get_device(self):
        return next(self.parameters()).device

    def cutoff(self, xs, thresh=None):
        eps = torch.finfo(xs.dtype).eps
        
        if not thresh is None:
            if eps < thresh:
                eps = thresh

        xs = xs.clamp(min=eps)

        if torch.any(torch.isnan(xs)):
            xs[torch.isnan(xs)] = eps

        return xs

    def softmax(self, xs):
        #xs = SoftmaxTransform()(xs)
        xs = dist.Multinomial(total_count=1, logits=xs).mean
        return xs
    
    def sigmoid(self, xs):
        #sigm_enc = nn.Sigmoid()
        #xs = sigm_enc(xs)
        #xs = clamp_probs(xs)
        xs = dist.Bernoulli(logits=xs).mean
        return xs

    def softmax_logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = self.softmax(xs)
        xs = torch.logit(xs, eps=eps)
        return xs

    def logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = torch.logit(xs, eps=eps)
        return xs

    def dirimulti_param(self, xs):
        xs = self.dirimulti_mass * self.sigmoid(xs)
        return xs

    def multi_param(self, xs):
        xs = self.softmax(xs)
        return xs

    def model1(self, xs):
        pyro.module('DensityFlow2', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)
        
        if self.loss_func=='negbinomial':
            total_count = pyro.param("inverse_dispersion", self.inverse_dispersion *
                                     xs.new_ones(self.input_size), constraint=constraints.positive)
            
        if self.use_zeroinflate:
            gate_logits = pyro.param("dropout_rate", xs.new_zeros(self.input_size))
            
        acs_scale = pyro.param("codebook_scale", xs.new_ones(self.latent_dim), constraint=constraints.positive)
        
        I = torch.eye(self.code_size)
        if self.latent_dist=='studentt':
            acs_dof,acs_loc = self.codebook(I)
        else:
            acs_loc = self.codebook(I)

        with pyro.plate('data'):
            prior = torch.zeros(batch_size, self.code_size, **self.options)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior))

            zn_loc = torch.matmul(ns,acs_loc)
            #zn_scale = torch.matmul(ns,acs_scale)
            zn_scale = acs_scale

            if self.latent_dist == 'studentt':
                prior_dof = torch.matmul(ns,acs_dof)
                zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1))
            elif self.latent_dist == 'laplacian':
                zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'cauchy':
                zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'normal':
                zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'gumbel':
                zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1))

            zs = zns
            concentrate = self.decoder_concentrate(zs)
            if self.loss_func in ['bernoulli']:
                log_theta = concentrate
            else:
                rate = concentrate.exp()
                theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
                if self.loss_func == 'poisson':
                    rate = theta * torch.sum(xs, dim=1, keepdim=True)

            if self.loss_func == 'negbinomial':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.NegativeBinomial(total_count=total_count, probs=theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.NegativeBinomial(total_count=total_count, probs=theta).to_event(1), obs=xs)
            elif self.loss_func == 'poisson':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'multinomial':
                #pyro.sample('x', dist.Multinomial(total_count=int(1e8), probs=theta), obs=xs)
                pyro.sample('x', dist.Multinomial(total_count=int(1e8), logits=concentrate), obs=xs)
            elif self.loss_func == 'bernoulli':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Bernoulli(logits=log_theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Bernoulli(logits=log_theta).to_event(1), obs=xs)

    def guide1(self, xs):
        with pyro.plate('data'):
            #zn_loc, zn_scale = self.encoder_zn(xs)
            zn_loc, zn_scale = self._get_basal_embedding(xs)
            zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))

            alpha = self.encoder_n(zns)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=alpha))

    def model2(self, xs, us=None):
        pyro.module('DensityFlow2', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)
        
        if self.loss_func=='negbinomial':
            #total_count = pyro.param("inverse_dispersion", self.inverse_dispersion *
            #                         xs.new_ones(self.input_size), constraint=constraints.positive)
            with pyro.plate("genes", self.input_size):
                inverse_dispersion = pyro.sample("inverse_dispersion", dist.LogNormal(self.inverse_dispersion, 0.5).to_event(1))
            
        if self.use_zeroinflate:
            gate_logits = pyro.param("dropout_rate", xs.new_zeros(self.input_size))
            
        acs_scale = pyro.param("codebook_scale", xs.new_ones(self.latent_dim), constraint=constraints.positive)

        I = torch.eye(self.code_size)
        if self.latent_dist=='studentt':
            acs_dof,acs_loc = self.codebook(I)
        else:
            acs_loc = self.codebook(I)

        with pyro.plate('data'):
            prior = torch.zeros(batch_size, self.code_size, **self.options)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior))

            zn_loc = torch.matmul(ns,acs_loc)
            #zn_scale = torch.matmul(ns,acs_scale)
            zn_scale = acs_scale

            if self.latent_dist == 'studentt':
                prior_dof = torch.matmul(ns,acs_dof)
                zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1))
            elif self.latent_dist == 'laplacian':
                zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'cauchy':
                zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'normal':
                zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
            elif self.latent_dist == 'gumbel':
                zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1))

            '''if self.cell_factor_size>0:
                zus = self._total_shifts(zns, us)
                zs = zns+zus
            else:
                zs = zns'''

            zs = zns
            concentrate = self.decoder_concentrate(zs)
            for i in np.arange(self.cell_factor_size):
                zus = self._cell_shift(zs, i, us[:,i].reshape(-1,1))
                concentrate += self.decoder_concentrate(zus)
                
            if self.loss_func in ['bernoulli']:
                log_theta = concentrate
            elif self.loss_func in ['negbinomial']:
                mu = concentrate.exp()
            else:
                rate = concentrate.exp()
                theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
                if self.loss_func == 'poisson':
                    rate = theta * torch.sum(xs, dim=1, keepdim=True)

            if self.loss_func == 'negbinomial':
                logits = (mu.log()-inverse_dispersion.log()).clamp(min=-10, max=10)
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.NegativeBinomial(total_count=inverse_dispersion, 
                                                                                         logits=logits),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.NegativeBinomial(total_count=inverse_dispersion, 
                                                           logits=logits).to_event(1), obs=xs)
            elif self.loss_func == 'poisson':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'multinomial':
                #pyro.sample('x', dist.Multinomial(total_count=int(1e8), probs=theta), obs=xs)
                pyro.sample('x', dist.Multinomial(total_count=int(1e8), logits=concentrate), obs=xs)
            elif self.loss_func == 'bernoulli':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Bernoulli(logits=log_theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Bernoulli(logits=log_theta).to_event(1), obs=xs)

    def guide2(self, xs, us=None):
        with pyro.plate('data'):
            #zn_loc, zn_scale = self.encoder_zn(xs)
            zn_loc, zn_scale = self._get_basal_embedding(xs)
            zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))

            alpha = self.encoder_n(zns)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=alpha))
            
            if self.loss_func == 'negbinomial':
                id_loc,id_scale = self.encoder_inverse_dispersion(zns)
                with pyro.plate("genes", self.input_size):
                    pyro.sample("inverse_dispersion", dist.LogNormal(id_loc, id_scale).to_event(1))

    def model3(self, xs, ys, embeds=None):
        pyro.module('DensityFlow2', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)
        
        if self.loss_func=='negbinomial':
            total_count = pyro.param("inverse_dispersion", self.inverse_dispersion *
                                     xs.new_ones(self.input_size), constraint=constraints.positive)
            
        if self.use_zeroinflate:
            gate_logits = pyro.param("dropout_rate", xs.new_zeros(self.input_size))
            
        acs_scale = pyro.param("codebook_scale", xs.new_ones(self.latent_dim), constraint=constraints.positive)

        I = torch.eye(self.code_size)
        if self.latent_dist=='studentt':
            acs_dof,acs_loc = self.codebook(I)
        else:
            acs_loc = self.codebook(I)

        with pyro.plate('data'):
            #prior = torch.zeros(batch_size, self.code_size, **self.options)
            prior = self.encoder_n(xs)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior), obs=ys)

            zn_loc = torch.matmul(ns,acs_loc)
            #prior_scale = torch.matmul(ns,acs_scale)
            zn_scale = acs_scale

            if self.latent_dist=='studentt':
                prior_dof = torch.matmul(ns,acs_dof)
                if embeds is None:
                    zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='laplacian':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='cauchy':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='normal':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.z_dist == 'gumbel':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1), obs=embeds)

            zs = zns

            concentrate = self.decoder_concentrate(zs)
            if self.loss_func in ['bernoulli']:
                log_theta = concentrate
            else:
                rate = concentrate.exp()
                theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
                if self.loss_func == 'poisson':
                    rate = theta * torch.sum(xs, dim=1, keepdim=True)

            if self.loss_func == 'negbinomial':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.NegativeBinomial(total_count=total_count, probs=theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.NegativeBinomial(total_count=total_count, probs=theta).to_event(1), obs=xs)
            elif self.loss_func == 'poisson':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'multinomial':
                #pyro.sample('x', dist.Multinomial(total_count=int(1e8), probs=theta), obs=xs)
                pyro.sample('x', dist.Multinomial(total_count=int(1e8), logits=concentrate), obs=xs)
            elif self.loss_func == 'bernoulli':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Bernoulli(logits=log_theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Bernoulli(logits=log_theta).to_event(1), obs=xs)

    def guide3(self, xs, ys, embeds=None):
        with pyro.plate('data'):
            if embeds is None:
                #zn_loc, zn_scale = self.encoder_zn(xs)
                zn_loc, zn_scale = self._get_basal_embedding(xs)
                zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
            else:
                zns = embeds

    def model4(self, xs, us, ys, embeds=None):
        pyro.module('DensityFlow2', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)
        
        if self.loss_func=='negbinomial':
            total_count = pyro.param("inverse_dispersion", self.inverse_dispersion *
                                     xs.new_ones(self.input_size), constraint=constraints.positive)
            
        if self.use_zeroinflate:
            gate_logits = pyro.param("dropout_rate", xs.new_zeros(self.input_size))
            
        acs_scale = pyro.param("codebook_scale", xs.new_ones(self.latent_dim), constraint=constraints.positive)

        I = torch.eye(self.code_size)
        if self.latent_dist=='studentt':
            acs_dof,acs_loc = self.codebook(I)
        else:
            acs_loc = self.codebook(I)

        with pyro.plate('data'):
            #prior = torch.zeros(batch_size, self.code_size, **self.options)
            prior = self.encoder_n(xs)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior), obs=ys)

            zn_loc = torch.matmul(ns,acs_loc)
            #prior_scale = torch.matmul(ns,acs_scale)
            zn_scale = acs_scale

            if self.latent_dist=='studentt':
                prior_dof = torch.matmul(ns,acs_dof)
                if embeds is None:
                    zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=zn_loc, scale=zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='laplacian':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Laplace(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='cauchy':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Cauchy(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.latent_dist=='normal':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1), obs=embeds)
            elif self.z_dist == 'gumbel':
                if embeds is None:
                    zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1))
                else:
                    zns = pyro.sample('zn', dist.Gumbel(zn_loc, zn_scale).to_event(1), obs=embeds)

            '''if self.cell_factor_size>0:
                zus = self._total_shifts(zns, us)
                zs = zns+zus
            else:
                zs = zns'''

            zs = zns
            concentrate = self.decoder_concentrate(zs)
            for i in np.arange(self.cell_factor_size):
                zus = self._cell_shift(zs, i, us[:,i].reshape(-1,1))
                concentrate += self.decoder_concentrate(zus)
            
            if self.loss_func in ['bernoulli']:
                log_theta = concentrate
            else:
                rate = concentrate.exp()
                theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
                if self.loss_func == 'poisson':
                    rate = theta * torch.sum(xs, dim=1, keepdim=True)

            if self.loss_func == 'negbinomial':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.NegativeBinomial(total_count=total_count, probs=theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.NegativeBinomial(total_count=total_count, probs=theta).to_event(1), obs=xs)
            elif self.loss_func == 'poisson':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'multinomial':
                #pyro.sample('x', dist.Multinomial(total_count=int(1e8), probs=theta), obs=xs)
                pyro.sample('x', dist.Multinomial(total_count=int(1e8), logits=concentrate), obs=xs)
            elif self.loss_func == 'bernoulli':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Bernoulli(logits=log_theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Bernoulli(logits=log_theta).to_event(1), obs=xs)

    def guide4(self, xs, us, ys, embeds=None):
        with pyro.plate('data'):
            if embeds is None:
                #zn_loc, zn_scale = self.encoder_zn(xs)
                zn_loc, zn_scale = self._get_basal_embedding(xs)
                zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))
            else:
                zns = embeds

    def _total_shifts(self, zns, us):
        zus = None
        for i in np.arange(self.cell_factor_size):
            if i==0:
                #if self.turn_off_cell_specific:
                #    zus = self.cell_factor_effect[i](us[:,i].reshape(-1,1))
                #else:
                #    zus = self.cell_factor_effect[i]([zns,us[:,i].reshape(-1,1)])
                zus = self._cell_shift(zns, i, us[:,i].reshape(-1,1))
            else:
                #if self.turn_off_cell_specific:
                #    zus = zus + self.cell_factor_effect[i](us[:,i].reshape(-1,1))
                #else:
                #    zus = zus + self.cell_factor_effect[i]([zns,us[:,i].reshape(-1,1)])
                zus = zus + self._cell_shift(zns, i, us[:,i].reshape(-1,1))
        return zus
                        
    def _get_codebook_identity(self):
        return torch.eye(self.code_size, **self.options)
    
    def _get_codebook(self):
        I = torch.eye(self.code_size, **self.options)
        if self.latent_dist=='studentt':
            _,cb = self.codebook(I)
        else:
            cb = self.codebook(I)
        return cb
    
    def get_codebook(self):
        """
        Return the mean part of metacell codebook
        """
        cb = self._get_codebook()
        cb = tensor_to_numpy(cb)
        return cb

    def _get_basal_embedding(self, xs):           
        loc, scale = self.encoder_zn(xs)
        return loc, scale 
    
    def get_basal_embedding(self, 
                             xs, 
                             batch_size: int = 1024):
        """
        Return cells' basal latent representations

        Parameters
        ----------
        xs
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor.
        batch_size
            Size of batch processing.
        use_decoder
            If toggled on, the latent representations will be reconstructed from the metacell codebook
        soft_assign
            If toggled on, the assignments of cells will use probabilistic values.
        """
        xs = self.preprocess(xs)
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                zns,_ = self._get_basal_embedding(X_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _code(self, xs):
        if self.supervised_mode:
            alpha = self.encoder_n(xs)
        else:
            #zns,_ = self.encoder_zn(xs)
            zns,_ = self._get_basal_embedding(xs)
            alpha = self.encoder_n(zns)
        return alpha
    
    def code(self, xs, batch_size=1024):
        xs = self.preprocess(xs)
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._code(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _soft_assignments(self, xs):
        alpha = self._code(xs)
        alpha = self.softmax(alpha)
        return alpha
    
    def soft_assignments(self, xs, batch_size=1024):
        """
        Map cells to metacells and return the probabilistic values of metacell assignments
        """
        xs = self.preprocess(xs)
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._soft_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _hard_assignments(self, xs):
        alpha = self._code(xs)
        res, ind = torch.topk(alpha, 1)
        ns = torch.zeros_like(alpha).scatter_(1, ind, 1.0)
        return ns
    
    def hard_assignments(self, xs, batch_size=1024):
        """
        Map cells to metacells and return the assigned metacell identities.
        """
        xs = self.preprocess(xs)
        xs = convert_to_tensor(xs, device=self.get_device())
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                a = self._hard_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def predict(self, xs, us, perturbs_predict:list, perturbs_reference:list, library_sizes=None):
        perturbs_reference = np.array(perturbs_reference)
        
        # basal embedding
        zs = self.get_basal_embedding(xs)
        for pert in perturbs_predict:
            pert_idx = int(np.where(perturbs_reference==pert)[0])
            us_i = us[:,pert_idx].reshape(-1,1)
            
            # factor effect of xs 
            dzs0 = self.get_cell_shift(zs, perturb_idx=pert_idx, perturb_us=us_i)
            
            # perturbation effect 
            ps = np.ones_like(us_i)
            if np.sum(np.abs(ps-us_i))>=1:
                dzs = self.get_cell_shift(zs, perturb_idx=pert_idx, perturb_us=ps)          
                zs = zs + dzs0 + dzs
            else:
                zs = zs + dzs0
        
        if library_sizes is None:
            library_sizes = np.sum(xs, axis=1, keepdims=True)
        elif type(library_sizes) == list:
            library_sizes = np.array(library_sizes)
            library_sizes = library_sizes.reshape(-1,1)
        elif len(library_sizes.shape)==1:
            library_sizes = library_sizes.reshape(-1,1)
            
        counts = self.get_counts(zs, library_sizes=library_sizes)
        
        return counts, zs
    
    def _cell_shift(self, zs, perturb_idx, perturb):
        #zns,_ = self.encoder_zn(xs)    
        #zns,_ = self._get_basal_embedding(xs)   
        zns = zs
        if perturb.ndim==2:
            if self.turn_off_cell_specific:
                ms = self.cell_factor_effect[perturb_idx](perturb)
            else:
                ms = self.cell_factor_effect[perturb_idx]([zns, perturb])
        else:
            if self.turn_off_cell_specific:
                ms = self.cell_factor_effect[perturb_idx](perturb.reshape(-1,1))
            else:
                ms = self.cell_factor_effect[perturb_idx]([zns, perturb.reshape(-1,1)])
            
        return ms 

    def get_cell_shift(self, 
                             zs, 
                             perturb_idx,
                             perturb_us,
                             batch_size: int = 1024):
        """
        Return cells' changes in the latent space induced by specific perturbation of a factor

        """
        #xs = self.preprocess(xs)
        zs = convert_to_tensor(zs, device=self.get_device())
        ps = convert_to_tensor(perturb_us, device=self.get_device())
        dataset = CustomDataset2(zs,ps)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for Z_batch, P_batch, _ in dataloader:
                zns = self._cell_shift(Z_batch, perturb_idx, P_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _get_theta(self, delta_zs):
        return self.decoder_concentrate(delta_zs)
    
    def get_theta(self, 
                             delta_zs, 
                             batch_size: int = 1024):
        """
        Return cells' changes in the feature space induced by specific perturbation of a factor

        """
        delta_zs = convert_to_tensor(delta_zs, device=self.get_device())
        dataset = CustomDataset(delta_zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        R = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for delta_Z_batch, _ in dataloader:
                r = self._get_theta(delta_Z_batch)
                R.append(tensor_to_numpy(r))
                pbar.update(1)

        R = np.concatenate(R)
        return R
    
    def _count(self, concentrate, library_size=None):
        if self.loss_func == 'bernoulli':
            #counts = self.sigmoid(concentrate)
            counts = dist.Bernoulli(logits=concentrate).to_event(1).mean
        elif self.loss_func == 'multinomial':
            theta = dist.Multinomial(total_count=int(1e8), logits=concentrate).mean
            counts = theta * library_size
        else:
            rate = concentrate.exp()
            theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
            counts = theta * library_size
        return counts
    
    def get_counts(self, concentrate, 
                   library_sizes,
                   batch_size: int = 1024):

        concentrate = convert_to_tensor(concentrate, device=self.get_device())
        
        if type(library_sizes) == list:
            library_sizes = np.array(library_sizes).reshape(-1,1)
        elif len(library_sizes.shape)==1:
            library_sizes = library_sizes.reshape(-1,1)
        ls = convert_to_tensor(library_sizes, device=self.get_device())
            
        dataset = CustomDataset2(concentrate,ls)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
        
        E = []
        with tqdm(total=len(dataloader), desc='', unit='batch') as pbar:
            for C_batch, L_batch, _ in dataloader:
                counts = self._count(C_batch, L_batch)
                E.append(tensor_to_numpy(counts))
                pbar.update(1)
        
        E = np.concatenate(E)
        return E
    
    def preprocess(self, xs, threshold=0):
        if self.loss_func == 'bernoulli':
            ad = sc.AnnData(xs)
            binarize(ad, threshold=threshold)
            xs = ad.X.copy()
        else:
            xs = np.round(xs)
            
        if sparse.issparse(xs):
            xs = xs.toarray()
        return xs 
    
    def fit(self, xs, 
            us = None, 
            ys = None,
            zs = None,
            num_epochs: int = 500, 
            learning_rate: float = 0.0001, 
            batch_size: int = 256, 
            algo: Literal['adam','rmsprop','adamw'] = 'adam', 
            beta_1: float = 0.9, 
            weight_decay: float = 0.005, 
            decay_rate: float = 0.9,
            config_enum: str = 'parallel',
            threshold: int = 0,
            use_jax: bool = True):
        """
        Train the DensityFlow2 model.

        Parameters
        ----------
        xs
            Single-cell experssion matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        us
            cell-level factor matrix. 
        ys
            Desired factor matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are desired factors.
        num_epochs
            Number of training epochs.
        learning_rate
            Parameter for training.
        batch_size
            Size of batch processing.
        algo
            Optimization algorithm.
        beta_1
            Parameter for optimization.
        weight_decay
            Parameter for optimization.
        decay_rate 
            Parameter for optimization.
        use_jax
            If toggled on, Jax will be used for speeding up. CAUTION: This will raise errors because of unknown reasons when it is called in
            the Python script or Jupyter notebook. It is OK if it is used when runing DensityFlow2 in the shell command.
        """
        xs = self.preprocess(xs, threshold=threshold)
        xs = convert_to_tensor(xs, dtype=self.dtype, device=self.get_device())
        if us is not None:
            us = convert_to_tensor(us, dtype=self.dtype, device=self.get_device())
        if ys is not None:
            ys = convert_to_tensor(ys, dtype=self.dtype, device=self.get_device())
        if zs is not None:
            zs = convert_to_tensor(zs, dtype=self.dtype, device=self.get_device())

        dataset = CustomDataset4(xs, us, ys, zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # setup the optimizer
        optim_params = {'lr': learning_rate, 'betas': (beta_1, 0.999), 'weight_decay': weight_decay}

        if algo.lower()=='rmsprop':
            optimizer = torch.optim.RMSprop
        elif algo.lower()=='adam':
            optimizer = torch.optim.Adam
        elif algo.lower() == 'adamw':
            optimizer = torch.optim.AdamW
        else:
            raise ValueError("An optimization algorithm must be specified.")
        scheduler = ExponentialLR({'optimizer': optimizer, 'optim_args': optim_params, 'gamma': decay_rate})

        pyro.clear_param_store()

        # set up the loss(es) for inference, wrapping the guide in config_enumerate builds the loss as a sum
        # by enumerating each class label form the sampled discrete categorical distribution in the model
        Elbo = JitTraceEnum_ELBO if use_jax else TraceEnum_ELBO
        elbo = Elbo(max_plate_nesting=1, strict_enumeration_warning=False)
        if us is None:
            if ys is None:
                guide = config_enumerate(self.guide1, config_enum, expand=True)
                loss_basic = SVI(self.model1, guide, scheduler, loss=elbo)
            else:
                guide = config_enumerate(self.guide3, config_enum, expand=True)
                loss_basic = SVI(self.model3, guide, scheduler, loss=elbo)
        else:
            if ys is None:
                guide = config_enumerate(self.guide2, config_enum, expand=True)
                loss_basic = SVI(self.model2, guide, scheduler, loss=elbo)
            else:
                guide = config_enumerate(self.guide4, config_enum, expand=True)
                loss_basic = SVI(self.model4, guide, scheduler, loss=elbo)

        # build a list of all losses considered
        losses = [loss_basic]
        num_losses = len(losses)

        with tqdm(total=num_epochs, desc='Training', unit='epoch') as pbar:
            for epoch in range(num_epochs):
                epoch_losses = [0.0] * num_losses
                for batch_x, batch_u, batch_y, batch_z, _ in dataloader:
                    if us is None:
                        batch_u = None
                    if ys is None:
                        batch_y = None
                    if zs is None:
                        batch_z = None

                    for loss_id in range(num_losses):
                        if batch_u is None:
                            if batch_y is None:
                                new_loss = losses[loss_id].step(batch_x)
                            else:
                                new_loss = losses[loss_id].step(batch_x, batch_y, batch_z)
                        else:
                            if batch_y is None:
                                new_loss = losses[loss_id].step(batch_x, batch_u)
                            else:
                                new_loss = losses[loss_id].step(batch_x, batch_u, batch_y, batch_z)
                        epoch_losses[loss_id] += new_loss

                avg_epoch_losses_ = map(lambda v: v / len(dataloader), epoch_losses)
                avg_epoch_losses = map(lambda v: "{:.4f}".format(v), avg_epoch_losses_)

                # store the loss
                str_loss = " ".join(map(str, avg_epoch_losses))

                # Update progress bar
                pbar.set_postfix({'loss': str_loss})
                pbar.update(1)
                
    @classmethod
    def save_model(cls, model, file_path, compression=False):
        """Save the model to the specified file path."""
        file_path = os.path.abspath(file_path)

        model.eval()
        if compression:
            with gzip.open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)
        else:
            with open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)

        print(f'Model saved to {file_path}')

    @classmethod
    def load_model(cls, file_path):
        """Load the model from the specified file path and return an instance."""
        print(f'Model loaded from {file_path}')

        file_path = os.path.abspath(file_path)
        if file_path.endswith('gz'):
            with gzip.open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        else:
            with open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        
        return model

        
EXAMPLE_RUN = (
    "example run: DensityFlow2 --help"
)

def parse_args():
    parser = argparse.ArgumentParser(
        description="DensityFlow2\n{}".format(EXAMPLE_RUN))

    parser.add_argument(
        "--cuda", action="store_true", help="use GPU(s) to speed up training"
    )
    parser.add_argument(
        "--jit", action="store_true", help="use PyTorch jit to speed up training"
    )
    parser.add_argument(
        "-n", "--num-epochs", default=200, type=int, help="number of epochs to run"
    )
    parser.add_argument(
        "-enum",
        "--enum-discrete",
        default="parallel",
        help="parallel, sequential or none. uses parallel enumeration by default",
    )
    parser.add_argument(
        "-data",
        "--data-file",
        default=None,
        type=str,
        help="the data file",
    )
    parser.add_argument(
        "-cf",
        "--cell-factor-file",
        default=None,
        type=str,
        help="the file for the record of cell-level factors",
    )
    parser.add_argument(
        "-bs",
        "--batch-size",
        default=1000,
        type=int,
        help="number of cells to be considered in a batch",
    )
    parser.add_argument(
        "-lr",
        "--learning-rate",
        default=0.0001,
        type=float,
        help="learning rate for Adam optimizer",
    )
    parser.add_argument(
        "-cs",
        "--codebook-size",
        default=100,
        type=int,
        help="size of vector quantization codebook",
    )
    parser.add_argument(
        "--z-dist",
        default='gumbel',
        type=str,
        choices=['normal','laplacian','studentt','gumbel','cauchy'],
        help="distribution model for latent representation",
    )
    parser.add_argument(
        "-zd",
        "--z-dim",
        default=10,
        type=int,
        help="size of the tensor representing the latent variable z variable",
    )
    parser.add_argument(
        "-likeli",
        "--likelihood",
        default='negbinomial',
        type=str,
        choices=['negbinomial', 'multinomial', 'poisson', 'bernoulli'],
        help="specify the distribution likelihood function",
    )
    parser.add_argument(
        "-zi",
        "--zeroinflate",
        action="store_true",
        help="use zero-inflated estimation",
    )
    parser.add_argument(
        "-id",
        "--inverse-dispersion",
        default=10.0,
        type=float,
        help="inverse dispersion prior for negative binomial",
    )
    parser.add_argument(
        "-hl",
        "--hidden-layers",
        nargs="+",
        default=[500],
        type=int,
        help="a tuple (or list) of MLP layers to be used in the neural networks "
        "representing the parameters of the distributions in our model",
    )
    parser.add_argument(
        "-hla",
        "--hidden-layer-activation",
        default='relu',
        type=str,
        choices=['relu','softplus','leakyrelu','linear'],
        help="activation function for hidden layers",
    )
    parser.add_argument(
        "-plf",
        "--post-layer-function",
        nargs="+",
        default=['layernorm'],
        type=str,
        help="post functions for hidden layers, could be none, dropout, layernorm, batchnorm, or combination, default is 'dropout layernorm'",
    )
    parser.add_argument(
        "-paf",
        "--post-activation-function",
        nargs="+",
        default=['none'],
        type=str,
        help="post functions for activation layers, could be none or dropout, default is 'none'",
    )
    parser.add_argument(
        "-64",
        "--float64",
        action="store_true",
        help="use double float precision",
    )
    parser.add_argument(
        "-dr",
        "--decay-rate",
        default=0.9,
        type=float,
        help="decay rate for Adam optimizer",
    )
    parser.add_argument(
        "--layer-dropout-rate",
        default=0.1,
        type=float,
        help="droput rate for neural networks",
    )
    parser.add_argument(
        "-b1",
        "--beta-1",
        default=0.95,
        type=float,
        help="beta-1 parameter for Adam optimizer",
    )  
    parser.add_argument(
        "--seed",
        default=None,
        type=int,
        help="seed for controlling randomness in this example",
    )
    parser.add_argument(
        "--save-model",
        default=None,
        type=str,
        help="path to save model for prediction",
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    assert (
        (args.data_file is not None) and (
            os.path.exists(args.data_file))
    ), "data file must be provided"

    if args.seed is not None:
        set_random_seed(args.seed)

    if args.float64:
        dtype = torch.float64
        torch.set_default_dtype(torch.float64)
    else:
        dtype = torch.float32
        torch.set_default_dtype(torch.float32)

    xs = dt.fread(file=args.data_file, header=True).to_numpy()
    us = None 
    if args.cell_factor_file is not None:
        us = dt.fread(file=args.cell_factor_file, header=True).to_numpy()

    input_size = xs.shape[1]
    cell_factor_size = 0 if us is None else us.shape[1]

    ###########################################
    df = DensityFlow2(
        input_size=input_size,
        cell_factor_size=cell_factor_size,
        inverse_dispersion=args.inverse_dispersion,
        z_dim=args.z_dim,
        hidden_layers=args.hidden_layers,
        hidden_layer_activation=args.hidden_layer_activation,
        use_cuda=args.cuda,
        config_enum=args.enum_discrete,
        use_zeroinflate=args.zeroinflate,
        loss_func=args.likelihood,
        nn_dropout=args.layer_dropout_rate,
        post_layer_fct=args.post_layer_function,
        post_act_fct=args.post_activation_function,
        codebook_size=args.codebook_size,
        z_dist = args.z_dist,
        dtype=dtype,
    )

    df.fit(xs, us=us, 
             num_epochs=args.num_epochs,
             learning_rate=args.learning_rate,
             batch_size=args.batch_size,
             beta_1=args.beta_1,
             decay_rate=args.decay_rate,
             use_jax=args.jit,
             config_enum=args.enum_discrete,
             )

    if args.save_model is not None:
        if args.save_model.endswith('gz'):
            DensityFlow2.save_model(df, args.save_model, compression=True)
        else:
            DensityFlow2.save_model(df, args.save_model)
    


if __name__ == "__main__":
    main()