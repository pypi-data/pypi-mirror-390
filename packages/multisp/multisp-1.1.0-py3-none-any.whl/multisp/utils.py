import scanpy as sc
import scipy
import scipy.sparse as sp
from typing import Optional
import torch
import torch.nn.functional as F
import numpy as np
import pandas as pd
import anndata
import sklearn
from sklearn.decomposition import PCA
import os
import random
from torch.backends import cudnn
from torch.distributions import Poisson
from sklearn.metrics import pairwise_distances



def set_seed(seed=42):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    cudnn.deterministic = True
    cudnn.benchmark = False
    
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8' 



def construct_graph_by_coordinate(cell_position, n_neighbors=3):
    nbrs = sklearn.neighbors.NearestNeighbors(n_neighbors=n_neighbors+1).fit(cell_position)  
    _ , indices = nbrs.kneighbors(cell_position)
    x = indices[:, 0].repeat(n_neighbors)
    y = indices[:, 1:].flatten()
    adj = pd.DataFrame(columns=['x', 'y', 'value'])
    adj['x'] = x
    adj['y'] = y
    adj['value'] = np.ones(x.size)
    n_spot = adj['x'].max() + 1
    adj = sp.coo_matrix((adj['value'], (adj['x'], adj['y'])), shape=(n_spot, n_spot))
    adj=adj.toarray()
    return adj


def clustering(adata, n_clusters, use_pca=True, n_comps=20, method='mclust', start=0.1, end=3.0, increment=0.01):
    if use_pca:
        pca= PCA(n_components=n_comps)
        z = pca.fit_transform(adata.obsm['MultiSP'])
        z = z.astype(z.dtype.newbyteorder('='))
        adata.obsm['MultiSP_pca']=z
    else:
        adata.obsm['MultiSP_pca']=adata.obsm['MultiSP']

    if method == 'mclust':
          adata = mclust_R(adata, use_rep='MultiSP_pca', num_cluster=n_clusters)
          adata.obs['MultiSP']=adata.obs['mclust']
    elif method == 'leiden':
          res = search_res(adata, n_clusters, use_rep='MultiSP_pca', method=method, start=start, end=end, increment=increment)
          sc.tl.leiden(adata, random_state=0, resolution=res)
          adata.obs['MultiSP']=adata.obs['leiden']
    elif method == 'louvain':
          res = search_res(adata, n_clusters, use_rep='MultiSP_pca', method=method, start=start, end=end, increment=increment)
          sc.tl.louvain(adata, random_state=0, resolution=res)
          adata.obs['MultiSP']=adata.obs['louvain']
          
    return adata

def mclust_R(adata, num_cluster, use_rep='MultiSP_pca', modelNames='EEE',random_seed=2020):
    """\
    Clustering using the mclust algorithm.
    The parameters are the same as those in the R package mclust.
    """
    
    np.random.seed(random_seed)
    import rpy2.robjects as robjects
    robjects.r.library("mclust")
 
    import rpy2.robjects.numpy2ri
    rpy2.robjects.numpy2ri.activate()
    r_random_seed = robjects.r['set.seed']
    r_random_seed(random_seed)
    rmclust = robjects.r['Mclust']

    res = rmclust(rpy2.robjects.numpy2ri.numpy2rpy(adata.obsm[use_rep]), num_cluster, modelNames)
    mclust_res = np.array(res[-2])
 
    adata.obs['mclust'] = mclust_res
    adata.obs['mclust'] = adata.obs['mclust'].astype('int')
    adata.obs['mclust'] = adata.obs['mclust'].astype('category')
    return adata

def search_res(adata, n_clusters, method='leiden', use_rep='emb', start=0.1, end=3.0, increment=0.01):
    '''\
    Searching corresponding resolution according to given cluster number
    
    Parameters
    ----------
    adata : anndata
        AnnData object of spatial data.
    n_clusters : int
        Targetting number of clusters.
    method : string
        Tool for clustering. Supported tools include 'leiden' and 'louvain'. The default is 'leiden'.    
    use_rep : string
        The indicated representation for clustering.
    start : float
        The start value for searching.
    end : float 
        The end value for searching.
    increment : float
        The step size to increase.
        
    Returns
    -------
    res : float
        Resolution.
        
    '''
    print('Searching resolution...')
    label = 0
    sc.pp.neighbors(adata, n_neighbors=50, use_rep=use_rep)
    for res in sorted(list(np.arange(start, end, increment)), reverse=True):
        if method == 'leiden':
           sc.tl.leiden(adata, random_state=0, resolution=res)
           count_unique = len(pd.DataFrame(adata.obs['leiden']).leiden.unique())
           print('resolution={}, cluster number={}'.format(res, count_unique))
        elif method == 'louvain':
           sc.tl.louvain(adata, random_state=0, resolution=res)
           count_unique = len(pd.DataFrame(adata.obs['louvain']).louvain.unique()) 
           print('resolution={}, cluster number={}'.format(res, count_unique))
        if count_unique == n_clusters:
            label = 1
            break

    assert label==1, "Resolution is not found. Please try bigger range or smaller step!." 
       
    return res    



def ZINBLoss(x, mean, disp, pi, scale_factor,ridge_lambda=0.5):
        eps = 1e-10
        mean = mean * scale_factor

        t1 = torch.lgamma(disp + eps) + torch.lgamma(x + 1.0) - torch.lgamma(x + disp + eps)
        t2 = (disp + x) * torch.log(1.0 + (mean / (disp + eps))) + (x * (torch.log(disp + eps) - torch.log(mean + eps)))
        nb_final = t1 + t2

        nb_case = nb_final - torch.log(1.0 - pi + eps)
        zero_nb = torch.pow(disp / (disp + mean + eps), disp)
        zero_case = -torch.log(pi + ((1.0 - pi) * zero_nb) + eps)
        result = torch.where(torch.le(x, 1e-8 * torch.ones_like(x)), zero_case, nb_case)

        if ridge_lambda > 0:
            ridge = ridge_lambda * torch.square(pi)
            result += ridge
        
        result = torch.mean(result)
        
        return result 

def ZIPLoss(x, pi, omega, scale_factor=1.0, ridge_lambda=0.5):
    eps = 1e-10
    lamb = omega * scale_factor
    if pi is not None:
        po_case = -Poisson(lamb).log_prob(x) - torch.log(1.0-pi+eps)
        zero_po = torch.exp(-lamb)
        zero_case = -torch.log(pi + ((1.0-pi)*zero_po) + eps)
        result = torch.where(torch.le(x, 1e-8), zero_case, po_case)
        
        if ridge_lambda > 0:
            ridge = ridge_lambda * torch.square(pi)
            result += ridge
        
        return torch.mean(result)
    
    else:
        result = -Poisson(lamb).log_prob(x)
        return torch.mean(result)

def NBLoss(x, mean, disp, scale_factor=1.0):
        eps = 1e-10
        mean = mean * scale_factor

        t1 = torch.lgamma(disp+eps) + torch.lgamma(x+1.0) - torch.lgamma(x+disp+eps)
        t2 = (disp+x) * torch.log(1.0 + (mean/(disp+eps))) + (x * (torch.log(disp+eps) - torch.log(mean+eps)))
        log_nb = t1 + t2
        #result = torch.mean(torch.sum(result, dim=1))
        result = torch.mean(log_nb)
        return result

def MixtureNBLoss(x, mean1, mean2, disp, pi_logits, scale_factor=None):
        eps = 1e-10
        if scale_factor is not None:
            scale_factor = scale_factor[:, None]
            mean1 = mean1 * scale_factor
            mean2 = mean2 * scale_factor
        t1 = torch.lgamma(disp+eps) + torch.lgamma(x+1.0) - torch.lgamma(x+disp+eps)
        t2_1 = (disp+x) * torch.log(1.0 + (mean1/(disp+eps))) + (x * (torch.log(disp+eps) - torch.log(mean1+eps)))
        log_nb_1 = t1 + t2_1

        t2_2 = (disp+x) * torch.log(1.0 + (mean2/(disp+eps))) + (x * (torch.log(disp+eps) - torch.log(mean2+eps)))
        log_nb_2 = t1 + t2_2

        logsumexp = torch.logsumexp(torch.stack((- log_nb_1, - log_nb_2 - pi_logits)), dim=0)
        softplus_pi = F.softplus(-pi_logits)

        log_mixture_nb = logsumexp - softplus_pi
        #result = torch.sum(-log_mixture_nb)
        result = torch.mean(-log_mixture_nb)
        return result

def clr_normalize_each_cell(adata, inplace=True):
    
    """Normalize count vector for each cell, i.e. for each row of .X"""

    import numpy as np
    import scipy

    def seurat_clr(x):
        # TODO: support sparseness
        s = np.sum(np.log1p(x[x > 0]))
        exp = np.exp(s / len(x))
        return np.log1p(x / exp)

    if not inplace:
        adata = adata.copy()
    
    # apply to dense or sparse matrix, along axis. returns dense matrix
    adata.X = np.apply_along_axis(
        seurat_clr, 1, (adata.X.toarray() if scipy.sparse.issparse(adata.X) else np.array(adata.X))
    )
    return adata     

def preprocess_graph(adj):
    adj = sp.coo_matrix(adj)
    adj_ = adj + sp.eye(adj.shape[0])
    rowsum = np.array(adj_.sum(1))
    degree_mat_inv_sqrt = sp.diags(np.power(rowsum, -0.5).flatten())
    adj_normalized = adj_.dot(degree_mat_inv_sqrt).transpose().dot(degree_mat_inv_sqrt).tocoo()
    adj_normalized=adj_normalized.toarray()
    return (adj_normalized)

def normalize_adj(adj):
    """Symmetrically normalize adjacency matrix."""
    adj = sp.coo_matrix(adj)
    rowsum = np.array(adj.sum(1))
    d_inv_sqrt = np.power(rowsum, -0.5).flatten()
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = sp.diags(d_inv_sqrt)
    adj = adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt)
    return adj.toarray()

def preprocess_adj(adj):
    """Preprocessing of adjacency matrix for simple GCN model and conversion to tuple representation."""
    adj_normalized = normalize_adj(adj)+np.eye(adj.shape[0])
    return adj_normalized 

def lsi(
        adata: anndata.AnnData, n_components: int = 20,
        use_highly_variable: Optional[bool] = None, **kwargs
       ) -> None:
    r"""
    LSI analysis (following the Seurat v3 approach)
    """
    if use_highly_variable is None:
        use_highly_variable = "highly_variable" in adata.var
    adata_use = adata[:, adata.var["highly_variable"]] if use_highly_variable else adata
    X = tfidf(adata_use.X)
    X_norm =X
    X_norm = np.log1p(X_norm * 1e4)
    X_lsi = sklearn.utils.extmath.randomized_svd(X_norm, n_components, **kwargs)[0]
    X_lsi -= X_lsi.mean(axis=1, keepdims=True)
    X_lsi /= X_lsi.std(axis=1, ddof=1, keepdims=True)
    adata.obsm["X_lsi"] = X_lsi[:,1:]

def tfidf(X):
    r"""
    TF-IDF normalization (following the Seurat v3 approach)
    """
    idf = X.shape[0] / X.sum(axis=0)
    if scipy.sparse.issparse(X):
        tf = X.multiply(1 / X.sum(axis=1))
        return tf.multiply(idf)
    else:
        tf = X / X.sum(axis=1, keepdims=True)
        return tf * idf   

def kl_loss(mu,sigma):
        return - 0.5 * torch.mean(1 + sigma - mu.pow(2) - sigma.exp()+1e-6)
        #return - 0.5 * torch.sum(1 + sigma - mu.pow(2) - sigma.exp()+1e-6)










    


 
 
