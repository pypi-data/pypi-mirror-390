import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from torch.distributions import LogNormal
from .module import GraphConvolution



class vae_Encoder(torch.nn.Module):
    def __init__(self,int_dim,out_dim):
        super(vae_Encoder,self).__init__()
        self.enc_mu=nn.Linear(int_dim, out_dim)
        self.enc_logvar=nn.Linear(int_dim, out_dim)
    
    def forward(self, x):
        mu=self.enc_mu(x)
        logvar=self.enc_logvar(x)
        return mu,logvar
    
class vae_Decoder(torch.nn.Module):
    def __init__(self,int_dim,out_dim):
        super(vae_Decoder,self).__init__()
        self.lin=nn.Linear(int_dim, out_dim)
    def forward(self, x):
        z=self.lin(x)
        return z



class ZINBDecoder(torch.nn.Module):
    def __init__(self, d_in,d_hid,d_out,dropout):
        super(ZINBDecoder, self).__init__()
        self.lin=nn.Sequential(nn.Linear(d_in, d_hid),
                                 nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=dropout)
                                )
        self.pi=nn.Linear(d_hid,d_out)

        self.disp=nn.Linear(d_hid,d_out)
        
        self.mean=nn.Linear(d_hid,d_out)
        
        self.DispAct = lambda x: torch.clamp(F.softplus(x), 1e-4, 1e4)
        self.MeanAct = lambda x: torch.clamp(torch.exp(x), 1e-5, 1e6)

    def forward(self,x):
        x=self.lin(x)
        pi= torch.sigmoid(self.pi(x))

        disp = self.DispAct(self.disp(x))

        mean = self.MeanAct(self.mean(x))
        
        return [pi, disp, mean]

class ZIPDecoder(torch.nn.Module):
    def __init__(self, d_in,d_hid,d_out,dropout):
        super(ZIPDecoder, self).__init__()
        self.lin=nn.Sequential(nn.Linear(d_in, d_hid),
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=dropout)
                                )
        self.pi=nn.Linear(d_hid,d_out)
        self.rho_output=nn.Linear(d_hid,d_out)
        self.peak_bias = nn.Parameter(torch.randn(1, d_out))
        nn.init.xavier_normal_(self.peak_bias)
        

    def forward(self,x):
        x=self.lin(x)
        pi= torch.sigmoid(self.pi(x))
        rho = self.rho_output(x)
        omega = F.softmax(rho+ self.peak_bias, dim=-1)
        return [pi,omega]

class BernoulliDecoder(torch.nn.Module):
    def __init__(self, d_in,d_hid,d_out):
        super(BernoulliDecoder, self).__init__()
        self.lin=nn.Sequential(nn.Linear(d_in, d_hid),
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0)
                                )
        self.out=nn.Linear(d_hid,d_out)
        self.peak_bias = nn.Parameter(torch.randn(1, d_out))
        nn.init.xavier_normal_(self.peak_bias)
       
    def forward(self,x):
        x=self.lin(x)
        x=F.sigmoid(self.out(x))*F.sigmoid(self.peak_bias)
        return x
    
class MixtureNBDecoder(torch.nn.Module):
    def __init__(self,d_in,d_hid,d_out,protein_back_mean,protein_back_scale,dropout):
        super(MixtureNBDecoder, self).__init__()
        if protein_back_mean is None and protein_back_scale is None:
            self.protein_back_log_mean = nn.Parameter(torch.randn(d_out), requires_grad=True)
            self.protein_back_log_scale = nn.Parameter(torch.log(torch.rand(d_out) + 0.5), requires_grad=True)
        else:
           self.protein_back_log_mean = nn.Parameter(protein_back_mean, requires_grad=True)
           self.protein_back_log_scale = nn.Parameter(torch.log(protein_back_scale), requires_grad=True)

        self.decoder=nn.Sequential(nn.Linear(d_in, d_hid),
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=dropout)
                                )

        self.alpha = nn.Sequential(nn.Linear(d_hid,d_out, nn.Softplus()))

        self.protein_back_log_mean_dec = nn.Linear(d_hid,d_out)
        self.protein_back_log_scale_dec = nn.Linear(d_hid,d_out)

        self.protein_back_prop_logit = nn.Linear(d_hid,d_out)

        
        self.protein_dec_disp = nn.Parameter(torch.randn(d_out), requires_grad=True)

       
    def forward(self,x):
        hidden=self.decoder(x)
        
        alpha = self.alpha(hidden)
        alpha =torch.clamp(alpha,1e-4, 1e4)

        protein_logit= self.protein_back_prop_logit(hidden)
        protein_back_prior = LogNormal(self.protein_back_log_mean, torch.exp(self.protein_back_log_scale))

        protein_back_log_mean = self.protein_back_log_mean_dec(hidden)
        protein_back_log_scale = torch.exp(self.protein_back_log_scale_dec(hidden))
        protein_back_postier = LogNormal(protein_back_log_mean, protein_back_log_scale)

        protein_background_mean = protein_back_postier.rsample()
        protein_forground_mean= (1+ alpha) *protein_background_mean
        
        protein_disp=torch.exp(torch.clamp(self.protein_dec_disp, -15., 15.)).unsqueeze(0)

        return [protein_background_mean,protein_forground_mean, protein_disp,protein_logit,protein_back_prior, protein_back_postier]


class NBDecoder(torch.nn.Module):
    def __init__(self, d_in,d_hid,d_out):
        super(NBDecoder, self).__init__()
        self.lin1=nn.Sequential(nn.Linear(d_in, d_hid),
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0)
                                )
        self.disp=nn.Linear(d_hid,d_out)
        self.mean=nn.Linear(d_hid,d_out)
        
        self.DispAct = lambda x: torch.clamp(F.softplus(x), 1e-4, 1e4)
        self.MeanAct = lambda x: torch.clamp(torch.exp(x), 1e-5, 1e6)

    def forward(self,x):
        x=self.lin1(x)
        disp = self.DispAct(self.disp(x))
        mean = self.MeanAct(self.mean(x))
       
        return [disp, mean]
    
class Encoder(torch.nn.Module):
    def __init__(self,d_in,d_out):
        super(Encoder, self).__init__()
        self.conv=GraphConvolution(d_in,d_out)
      
    def forward(self, x, adj):
        x=self.conv(x,adj)
        return x

class Pro_Decoder(torch.nn.Module):
    def __init__(self,d_in,d_hid,d_out):
        super(Pro_Decoder, self).__init__()
        self.lin=nn.Sequential(nn.Linear(d_in, d_hid), 
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(d_hid,d_out)
                                )
                                 
        self.MeanAct = lambda x: torch.clamp(torch.exp(x), 1e-5, 1e6)
      
    def forward(self,x):
        x=self.lin(x)
        x=self.MeanAct(x)
        return x
    

class Decoder(torch.nn.Module):
    def __init__(self,d_in,d_hid,d_out):
        super(Decoder, self).__init__()
        self.lin=nn.Sequential(nn.Linear(d_in, d_hid), 
                                nn.BatchNorm1d(d_hid),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(d_hid,d_out)
                                )
                               
    def forward(self,x):
        x=self.lin(x)
        return x
    
class Net_RNA(torch.nn.Module):
    def __init__(self,in_dims,decoder_type='ZINB'):
        super(Net_RNA,self).__init__()
        [dim_1,dim_2,dim_3] = in_dims
        self.decoder_type=decoder_type
        self.dropout=0.0
        self.encoder=Encoder(100,dim_3)
        self.vaencoder=vae_Encoder(dim_3,dim_3)
        if self.decoder_type=='ZINB':
           self.decoder=ZINBDecoder(dim_3,dim_2,dim_1,self.dropout)
        if self.decoder_type=='NB':
           self.decoder=NBDecoder(dim_3,dim_2,dim_1)
        if self.decoder_type=='MSE':
           self.decoder=Decoder(dim_3,dim_2,dim_1)
        

    def forward(self,feat,adj):
        z= self.encoder(feat,adj)
        z=F.elu(z)
        z=F.dropout(z,p=self.dropout,training=self.training)
        mu,logvar=self.vaencoder(z)
        z=self.reparametrize(mu,logvar)

        decoder_results=self.decoder(z)

        return z,mu,logvar,decoder_results


    def reparametrize(self, mu, sigma):
        sigma = torch.exp(sigma/2)
        eps = torch.randn_like(sigma)
        if self.training:
           z = mu + eps * sigma
        else:
           z=mu
        return z

class Net_ATAC(torch.nn.Module):
    def __init__(self,in_dims,decoder_type='ZIP'):
        super(Net_ATAC,self).__init__()
        [dim_1,dim_2,dim_3] = in_dims
        self.dropout=0.0
        self.decoder_type=decoder_type


        if self.decoder_type=='MSE':
           self.encoder=Encoder(50,dim_3)
        else:
           self.encoder=Encoder(100,dim_3)

        self.vaencoder=vae_Encoder(dim_3,dim_3)
        if self.decoder_type=='ZIP':
           self.decoder=ZIPDecoder(dim_3,dim_2,dim_1,self.dropout)
        if self.decoder_type=='Bernoulli':
           self.decoder=BernoulliDecoder(dim_3,dim_2,dim_1)
        if self.decoder_type=='MSE':
           self.decoder=Decoder(dim_3,dim_2,dim_1)

    def forward(self,feat,adj):
        z= self.encoder(feat,adj)

        z=F.elu(z)
        z=F.dropout(z,p=self.dropout,training=self.training)
        mu,logvar=self.vaencoder(z)
        z=self.reparametrize(mu,logvar)

        decoder_results=self.decoder(z)
          
        return z,mu,logvar,decoder_results
    
    def reparametrize(self, mu, sigma):
        sigma = torch.exp(sigma/2)
        eps = torch.randn_like(sigma)
        if self.training:
           z = mu + eps * sigma
        else:
           z=mu
        return z


class Net_Protein(torch.nn.Module):
    def __init__(self,in_dims,decoder_type='MSE',protein_back_mean=None,protein_back_scale=None):
        super(Net_Protein,self).__init__()
        [dim_1,dim_2,dim_3] = in_dims
        self.decoder_type=decoder_type
        self.dropout=0.0
        self.encoder=Encoder(dim_1,dim_3)
        self.vaencoder=vae_Encoder(dim_3,dim_3)
        
        if self.decoder_type=='MSE':
           self.decoder=Pro_Decoder(dim_3,dim_2,dim_1)
        if self.decoder_type=='NB':
           self.decoder=NBDecoder(dim_3,dim_2,dim_1)
        if self.decoder_type=='MixtureNB':
           self.decoder=MixtureNBDecoder(dim_3,dim_2,dim_1,protein_back_mean,protein_back_scale,self.dropout)

    def forward(self,feat,adj):
        z=self.encoder(feat,adj)
        z=F.elu(z)
        z=F.dropout(z,p=self.dropout,training=self.training)
        mu,logvar=self.vaencoder(z)
        z=self.reparametrize(mu,logvar)

        decoder_results=self.decoder(z)

    
        return z,mu,logvar,decoder_results
    
    def reparametrize(self, mu, sigma):
        sigma = torch.exp(sigma/2)
        eps = torch.randn_like(sigma)
        if self.training:
           z = mu + eps * sigma
        else:
           z=mu
        return z

class Net_Image(torch.nn.Module):
    def __init__(self,in_dims):
        super(Net_Image,self).__init__()
        [dim_1,dim_2,dim_3] = in_dims
        self.encoder=Encoder(dim_1,dim_3)
        self.vaencoder=vae_Encoder(dim_3,dim_3)

        self.decoder=Decoder(dim_3,dim_2,dim_1)

    def forward(self,feat,adj):
        z=self.encoder(feat,adj)
        z=F.elu(z)
        z=F.dropout(z,p=0.0,training=self.training)
        mu,logvar=self.vaencoder(z)
        z=self.reparametrize(mu,logvar)
        x_rec=self.decoder(z)
        
        return z,mu,logvar,x_rec
        
    def reparametrize(self, mu, sigma):
        sigma = torch.exp(sigma/2)
        eps = torch.randn_like(sigma)
        if self.training:
           z = mu + eps * sigma
        else:
           z=mu
        return z


class Net_omic_fusion_RNA_ATAC(torch.nn.Module):
    def __init__(self,omic1_in_dims,omic2_in_dims,pre_model_1,pre_model_2,decoder_type1,decoder_type2):
        super(Net_omic_fusion_RNA_ATAC,self).__init__()
        self.omic1= Net_RNA(omic1_in_dims,decoder_type=decoder_type1)
        self.omic2= Net_ATAC(omic2_in_dims,decoder_type=decoder_type2)
        if decoder_type2=='MSE':
           self.fusion=nn.Linear(omic1_in_dims[2]+omic2_in_dims[2],omic1_in_dims[2])
        else:
           self.fusion=nn.Sequential(nn.Linear(omic1_in_dims[2]+omic2_in_dims[2], omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2])
                                )
        self.load_pretrained(pre_model_1,pre_model_2)

    
    def load_pretrained(self,pre_model_1,pre_model_2):
        self.omic1.load_state_dict(pre_model_1.state_dict())
        self.omic2.load_state_dict(pre_model_2.state_dict())

       
    def forward(self,feat1,feat2,adj_1,adj_2):
        z1,mu1,logvar1,_=self.omic1(feat1,adj_1)
        z2,mu2,logvar2,_=self.omic2(feat2,adj_2)
        
        z=self.fusion(torch.cat((z1,z2),dim=1))

        decoder_results1=self.omic1.decoder(z)
        decoder_results2=self.omic2.decoder(z)
        
        results = {'emb_latent_omics1':z1,
                       'emb_latent_omics2':z2,
                       'emb_latent_fusion':z,
                     
                     'decoder_results1':decoder_results1,
                     'decoder_results2':decoder_results2,
                      }
        return results,mu1,logvar1,mu2,logvar2
       

class Net_omic_fusion_RNA_Protein(torch.nn.Module):
    def __init__(self,omic1_in_dims,omic2_in_dims,pre_model_1,pre_model_2,decoder_type1,decoder_type2):
        super(Net_omic_fusion_RNA_Protein,self).__init__()
        self.omic1= Net_RNA(omic1_in_dims,decoder_type=decoder_type1)
        self.omic2= Net_Protein(omic2_in_dims,decoder_type=decoder_type2)
        self.fusion=nn.Sequential(nn.Linear(omic1_in_dims[2]+omic2_in_dims[2], omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2])
                                )
        self.load_pretrained(pre_model_1,pre_model_2)

    
    def load_pretrained(self,pre_model_1,pre_model_2):
        self.omic1.load_state_dict(pre_model_1.state_dict())
        self.omic2.load_state_dict(pre_model_2.state_dict())

       
    def forward(self,feat1,feat2,adj_1,adj_2):
          z1,mu1,logvar1,_=self.omic1(feat1,adj_1)
          z2,mu2,logvar2,_=self.omic2(feat2,adj_2)
          z=self.fusion(torch.cat((z1,z2),dim=1))
          decoder_results1=self.omic1.decoder(z)

          decoder_results2=self.omic2.decoder(z)

          results = {'emb_latent_omics1':z1,
                       'emb_latent_omics2':z2,
                       'emb_latent_fusion':z,
                      'decoder_results1':decoder_results1,
                      'decoder_results2':decoder_results2,
                       }
          return results,mu1,logvar1,mu2,logvar2

class Net_omic_fusion_RNA_Protein_Image(torch.nn.Module):
    def __init__(self,omic1_in_dims,omic2_in_dims,omic3_in_dims,pre_model_1,pre_model_2,pre_model_3,decoder_type1,decoder_type2):
        super(Net_omic_fusion_RNA_Protein_Image,self).__init__()
        self.omic1= Net_RNA(omic1_in_dims,decoder_type=decoder_type1)
        self.omic2= Net_Protein(omic2_in_dims,decoder_type=decoder_type2)
        self.omic3= Net_Image(omic3_in_dims)
        self.fusion=nn.Sequential(nn.Linear(omic1_in_dims[2]+omic2_in_dims[2]+omic3_in_dims[2], omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2]),
                                nn.BatchNorm1d(omic1_in_dims[2]),
                                nn.ELU(inplace=True),
                                nn.Dropout(p=0.0),
                                nn.Linear(omic1_in_dims[2],omic1_in_dims[2])
                                )
        self.load_pretrained(pre_model_1,pre_model_2,pre_model_3)

    
    def load_pretrained(self,pre_model_1,pre_model_2,pre_model_3):
        self.omic1.load_state_dict(pre_model_1.state_dict())
        self.omic2.load_state_dict(pre_model_2.state_dict())
        self.omic3.load_state_dict(pre_model_3.state_dict())

       
    def forward(self,feat1,feat2,feat3,adj_1,adj_2,adj_3):
          z1,mu1,logvar1,_=self.omic1(feat1,adj_1)
          
          z2,mu2,logvar2,_=self.omic2(feat2,adj_2)
          z3,mu3,logvar3,x_rec3=self.omic3(feat3,adj_3)

          z=self.fusion(torch.cat((z1,z2,z3),dim=1))
      
          decoder_results1=self.omic1.decoder(z)

          decoder_results2=self.omic2.decoder(z)

          x_rec3=self.omic3.decoder(z)

          results = {'emb_latent_omics1':z1,
                       'emb_latent_omics2':z2,
                       'emb_latent_omics3':z3,
                       'emb_latent_fusion':z,


                       'decoder_results1':decoder_results1,
                        'decoder_results2':decoder_results2,
                        'emb_recon_omics3':x_rec3
                       }
          return results,mu1,logvar1,mu2,logvar2,mu3,logvar3





