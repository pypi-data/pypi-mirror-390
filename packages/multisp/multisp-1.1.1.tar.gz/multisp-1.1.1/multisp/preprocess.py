import torch
import numpy as np
import scanpy as sc
import episcanpy as epi
from scipy.sparse import issparse
from sklearn.decomposition import PCA
from sklearn.neighbors import kneighbors_graph 
from .utils import construct_graph_by_coordinate,preprocess_graph,clr_normalize_each_cell,lsi,tfidf
    
def data_preprocess(adata_omics1, adata_omics2,modality_type='RNA and ATAC', k=3,lamda=0,pro_decoder_type='MSE',atac_decoder_type='ZIP'): 
    adata_omics1=RNA_preprocess(adata_omics1)
   
    if modality_type=='RNA and Protein':
       adata_omics2=Protein_preprocess(adata_omics2,decoder_type=pro_decoder_type)
      
    if modality_type=='RNA and ATAC':
       adata_omics2=ATAC_preprocess(adata_omics2,decoder_type=atac_decoder_type)

    if modality_type=='RNA_Protein_Image':
       adata_omics2=Protein_preprocess(adata_omics2,decoder_type=pro_decoder_type)
       adata_omics2.obsm['image_feat']= Image_preprocess(adata_omics2.obsm['image_feature'])

  
       
    adata_omics1,adata_omics2=graph_construction(adata_omics1,adata_omics2,k,lamda)

   
    if modality_type=='RNA_Protein_Image':
         adata_omics2.obsm['adj_image_combined']=preprocess_graph(lamda*graph_construction_iamge(adata_omics2.obsm['image_feat'])+(1-lamda)*adata_omics2.obsm['adj_spatial'])
         
    return adata_omics1,adata_omics2

    
def RNA_preprocess(adata):
       sc.pp.filter_genes(adata, min_cells=10)
       sc.pp.highly_variable_genes(adata, flavor="seurat_v3", n_top_genes=3000)
      
       adata.obsm['count']=adata.X
       sc.pp.normalize_per_cell(adata)
       adata.obs['size_factors'] = adata.obs.n_counts/ np.median(adata.obs.n_counts)

       sc.pp.log1p(adata)

       adata.obsm['normalized']=adata.X

       sc.pp.scale(adata)
       
       adata.obsm['count']=adata.obsm['count'][:, adata.var['highly_variable']]
       adata.obsm['normalized'] = adata.obsm['normalized'][:, adata.var['highly_variable']]
       adata= adata[:, adata.var['highly_variable']]

       if issparse(adata.X):
           adata.X=adata.X.toarray()
       if issparse(adata.obsm['count']):
           adata.obsm['count']=adata.obsm['count'].toarray()
       if issparse(adata.obsm['normalized']):
           adata.obsm['normalized']=adata.obsm['normalized'].toarray() 
      
       adata.obsm['feat'] =PCA(n_components=100, random_state=42).fit_transform(adata.X)

       return adata
    
def Protein_preprocess(adata,decoder_type='MSE'):
        adata.obsm['count']=adata.X

        if issparse(adata.X):
           adata.X=adata.X.toarray()
        if issparse(adata.obsm['count']):
           adata.obsm['count']=adata.obsm['count'].toarray()

        if decoder_type=='MixtureNB':
            X_norm=np.log1p(adata.X)
            from sklearn.mixture import GaussianMixture
            gm = GaussianMixture(n_components=2, covariance_type="diag", n_init=20).fit(X_norm)
            back_idx = np.argmin(gm.means_, axis=0)
            protein_log_back_mean = np.log(np.expm1(gm.means_[back_idx, np.arange(adata.n_vars)]))
            protein_log_back_scale = np.sqrt(gm.covariances_[back_idx, np.arange(adata.n_vars)])
            adata.uns['protein_log_back_mean']=protein_log_back_mean 
            adata.uns[' protein_log_back_scale']= protein_log_back_scale
            adata= clr_normalize_each_cell(adata)
            adata.obs['size_factors'] =1.0
       

        if decoder_type=='NB':
            raw_n_counts=adata.X.sum(axis=1)
            adata.obs['size_factors'] =raw_n_counts
            adata= clr_normalize_each_cell(adata)
      
        if decoder_type=='MSE':
            adata= clr_normalize_each_cell(adata)
            adata.obs['size_factors'] =1.0


        adata.obsm['feat']=adata.X

        return adata
 

def ATAC_preprocess(adata,decoder_type='ZIP'):
        
        if decoder_type=='MSE':
             if 'X_lsi' not in adata.obsm.keys():
                 lsi(adata, use_highly_variable=False, n_components=50+1)

        else:
            import episcanpy as epi

            epi.pp.filter_features(adata, min_cells=int(adata.shape[0] * 0.03))
            epi.pp.filter_features(adata, min_cells=1)
            adata.obsm['count']=adata.X

            if decoder_type=='ZIP':
               adata.obs['size_factors'] = np.sum(adata.X,axis=1)
               lsi(adata, use_highly_variable=False, n_components=100+1)
            
            if decoder_type=='Bernoulli':
               lsi(adata, use_highly_variable=False, n_components=100+1)
               adata.X[adata.X>0] = 1
               

            if issparse(adata.X):
               adata.X=adata.X.toarray()
            if issparse(adata.obsm['count']):
               adata.obsm['count']=adata.obsm['count'].toarray()

        adata.obsm['feat']=adata.obsm['X_lsi'].copy()

        
        return adata

def Image_preprocess(X):
      #   from sklearn.preprocessing import StandardScaler
      #   scaler = StandardScaler()
      #   X= scaler.fit_transform(X)

        #feature=PCA(n_components=100, random_state=42).fit_transform(X)
        feature=X
 
        return feature

def graph_construction(adata1,adata2,k,lamda):
        adj=construct_graph_by_coordinate(adata1.obsm['spatial'],k)
        adj = adj + adj.T
        adj = np.where(adj>1, 1, adj)

        adj_feature_omic1=kneighbors_graph(adata1.obsm['feat'], 20, mode="connectivity", metric="cosine", include_self=False)
        adj_feature_omic2=kneighbors_graph(adata2.obsm['feat'], 20, mode="connectivity", metric="cosine", include_self=False)


        adj_feature_omic1=adj_feature_omic1.toarray()
        adj_feature_omic2=adj_feature_omic2.toarray()

        adj_feature_omic1 = adj_feature_omic1 + adj_feature_omic1.T
        adj_feature_omic1 = np.where(adj_feature_omic1>1, 1, adj_feature_omic1)
        
        adj_feature_omic2 = adj_feature_omic2 + adj_feature_omic2.T
        adj_feature_omic2 = np.where(adj_feature_omic2>1, 1, adj_feature_omic2)
    
       

        adata1.obsm['adj_spatial']=adj
        adata2.obsm['adj_spatial']=adj

  
        adata1.obsm['adj_combined']=preprocess_graph((1-lamda)*adj+lamda*adj_feature_omic1)
        adata2.obsm['adj_combined']=preprocess_graph((1-lamda)*adj+lamda*adj_feature_omic2)

        return adata1,adata2

def graph_construction_iamge(X):
       
        adj_feature=kneighbors_graph(X, 20, mode="connectivity", metric="cosine", include_self=False)
        adj_feature=adj_feature.toarray()
        adj_feature = adj_feature + adj_feature.T
        adj_feature = np.where(adj_feature>1, 1, adj_feature)

        return adj_feature

   
 


   
 