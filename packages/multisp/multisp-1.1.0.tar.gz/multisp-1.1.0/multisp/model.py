import torch
import torch.nn as nn
from .layer import Net_RNA,Net_ATAC,Net_Protein,Net_omic_fusion_RNA_ATAC,Net_omic_fusion_RNA_Protein,Net_Image,Net_omic_fusion_RNA_Protein_Image
from .module import GAN_Discriminator,GAN_Discriminator_Tri_modality
from tqdm import tqdm
import torch.nn.functional as F
from .utils import kl_loss,ZINBLoss,ZIPLoss,NBLoss,MixtureNBLoss
from .preprocess import data_preprocess
from torch.distributions.kl import kl_divergence
from .utils import set_seed

class MultiSP(nn.Module):
    def __init__(
            self,
            data,
            lamda=0,
            ad_weight=0.1,
            k_neighbors: int = 3,
            data_type='10x',
            device= torch.device('cpu'),
            random_seed = 42,
            modality_type='RNA and Protein',
            decoder_type1='ZINB',
            decoder_type2='MSE',
            ):
        super(MultiSP, self).__init__()
        self.data = data.copy()
        self.data_type=data_type
        self.device = device
        self.random_seed = random_seed
        self.k_neighbors=k_neighbors
        self.lamda=lamda
        self.modality_type=modality_type
        self.decoder_type1=decoder_type1
        self.decoder_type2=decoder_type2
        self.ad_weight=ad_weight

        self.adata_omic1=self.data['adata_omics1'].copy()
        self.adata_omic2=self.data['adata_omics2'].copy()


        
        if self.data_type=='10x':
           self.loss_weight=[1,1,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=100
           self.epoch=50
           self.weight_decay=0.0

        if self.data_type=='Spatial_ATAC_RNA_seq':
           self.ad_weight=0.01
           self.loss_weight=[1,10,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005

           if self.decoder_type2=='MSE':
               self.pre_epoch=50
               self.epoch=50
               
           if self.decoder_type2=='ZIP':
               self.pre_epoch=100
               self.epoch=100

           self.weight_decay=0

        if self.data_type=='MISAR_seq':
           self.loss_weight=[1,5,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=100
           self.epoch=100
           self.weight_decay=1e-5

        if self.data_type=='SPOTS':
           self.loss_weight=[1,1,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=100
           self.epoch=50
           self.weight_decay=0.0

        if self.data_type=='Spatial_CITE_Seq':
           self.ad_weight=0.1
           self.loss_weight=[1,1,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=100
           self.epoch=50
           self.weight_decay=0.0

        if self.data_type=='Spatial_DBIT_Seq':
           self.ad_weight=0.1
           self.loss_weight=[1,1,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=100
           self.epoch=50
           self.weight_decay=0.0

        if self.modality_type=='RNA_Protein_Image':
           self.loss_weight=[1,1,1,1]
           self.learning_rate=0.001
           self.d_learning_rate=0.005
           self.pre_epoch=300
           self.epoch=300
           self.weight_decay=0.0
         

        set_seed(random_seed)
         
        if self.modality_type=='RNA and Protein' or self.modality_type=='RNA_Protein_Image':
           self.pro_decoder_type=self.decoder_type2
           self.adata_omic1,self.adata_omic2=data_preprocess(self.adata_omic1,self.adata_omic2,self.modality_type,self.k_neighbors,lamda=self.lamda,
                                                          pro_decoder_type=self.pro_decoder_type)
           
        if self.modality_type=='RNA and ATAC':
           self.atac_decoder_type=self.decoder_type2
           self.adata_omic1,self.adata_omic2=data_preprocess(self.adata_omic1,self.adata_omic2,self.modality_type,self.k_neighbors,lamda=self.lamda,
                                                          atac_decoder_type=self.atac_decoder_type)
      
        self.feature1=torch.tensor(self.adata_omic1.obsm['feat'],dtype=torch.float32).to(self.device)

        if self.decoder_type1=='ZINB' or self.decoder_type1=='NB':
            self.feature1_raw=torch.tensor(self.adata_omic1.obsm['count'],dtype=torch.float32).to(self.device)
            self.scale_factor1=torch.tensor(self.adata_omic1.obs['size_factors'], dtype=torch.float32).unsqueeze(1).to(self.device)
            self.in_dim_1 =[self.feature1_raw.shape[1],1024,128]
        
        if self.decoder_type1=='MSE':
           self.feature1_normalized=torch.tensor(self.adata_omic1.obsm['normalized'],dtype=torch.float32).to(self.device)
           self.in_dim_1 =[self.feature1_normalized.shape[1],1024,128]

        self.adj_1=torch.tensor(self.adata_omic1.obsm['adj_combined'],dtype=torch.float32).to(self.device)
        

        if self.modality_type=='RNA and Protein':
           self.feature2_raw=torch.tensor(self.adata_omic2.obsm['count'],dtype=torch.float32).to(self.device)
           self.feature2=torch.tensor(self.adata_omic2.obsm['feat'],dtype=torch.float32).to(self.device)
           self.scale_factor2=torch.tensor(self.adata_omic2.obs['size_factors'], dtype=torch.float32).unsqueeze(1).to(self.device)
           self.adj_2=torch.tensor(self.adata_omic2.obsm['adj_combined'],dtype=torch.float32).to(self.device)
           self.in_dim_2=[self.feature2_raw.shape[1],256,128]
           
           if self.decoder_type2=='MixtureNB':
               self.protein_log_back_mean=torch.tensor(self.adata_omic2.uns['protein_log_back_mean'],dtype=torch.float32).to(self.device)
               self.protein_log_back_scale=torch.tensor(self.adata_omic2.uns[' protein_log_back_scale'],dtype=torch.float32).to(self.device)

        if self.modality_type=='RNA and ATAC':
           self.feature2=torch.tensor(self.adata_omic2.obsm['feat'],dtype=torch.float32).to(self.device)
           if self.decoder_type2=='MSE':
              self.in_dim_2=[self.feature2.shape[1],50,128]

           if self.decoder_type2=='ZIP':
              self.feature2_raw=torch.tensor(self.adata_omic2.obsm['count'],dtype=torch.float32).to(self.device)
              self.scale_factor2=torch.tensor(self.adata_omic2.obs['size_factors'], dtype=torch.float32).unsqueeze(1).to(self.device)
              self.in_dim_2=[self.feature2_raw.shape[1],1024,128]

           if self.decoder_type2=='Bernoulli':
              self.feature2_binarized=torch.tensor(self.adata_omic2.X,dtype=torch.float32).to(self.device)
              self.in_dim_2=[self.feature2_binarized.shape[1],1024,128]

           self.adj_2=torch.tensor(self.adata_omic2.obsm['adj_combined'],dtype=torch.float32).to(self.device)

        if modality_type=='RNA_Protein_Image':
           self.feature2_raw=torch.tensor(self.adata_omic2.obsm['count'],dtype=torch.float32).to(self.device)
           self.feature2=torch.tensor(self.adata_omic2.obsm['feat'],dtype=torch.float32).to(self.device)
           self.scale_factor2=torch.tensor(self.adata_omic2.obs['size_factors'],dtype=torch.float32).unsqueeze(1).to(self.device)
           self.adj_2=torch.tensor(self.adata_omic2.obsm['adj_combined'],dtype=torch.float32).to(self.device)
           self.in_dim_2=[self.feature2_raw.shape[1],256,128]
     
           if self.decoder_type2=='MixtureNB':
                     self.protein_log_back_mean=torch.tensor(self.adata_omic2.uns['protein_log_back_mean'],dtype=torch.float32).to(self.device)
                     self.protein_log_back_scale=torch.tensor(self.adata_omic2.uns[' protein_log_back_scale'],dtype=torch.float32).to(self.device)
            
           
           self.feature3=torch.tensor(self.adata_omic2.obsm['image_feat'],dtype=torch.float32).to(self.device)
           self.in_dim_3=[self.feature3.shape[1],100,128]

           self.adj_3=torch.tensor(self.adata_omic2.obsm['adj_image_combined'],dtype=torch.float32).to(self.device)


         
    def train(self):
        if self.modality_type=='RNA and Protein':
           self.model_omic1=Net_RNA(self.in_dim_1,decoder_type=self.decoder_type1).to(self.device)

           if self.decoder_type2=='MixtureNB':
                self.model_omic2=Net_Protein(self.in_dim_2,
                                             protein_back_mean=self.protein_log_back_mean,
                                             protein_back_scale=self.protein_log_back_scale,
                                             decoder_type=self.decoder_type2).to(self.device)
           self.model_omic2=Net_Protein(self.in_dim_2,decoder_type=self.decoder_type2).to(self.device)

        if self.modality_type=='RNA and ATAC':
           self.model_omic1=Net_RNA(self.in_dim_1,decoder_type=self.decoder_type1).to(self.device)
           self.model_omic2=Net_ATAC(self.in_dim_2,decoder_type=self.decoder_type2).to(self.device)


        if self.modality_type=='RNA_Protein_Image':
            self.model_omic1=Net_RNA(self.in_dim_1,decoder_type=self.decoder_type1).to(self.device)

            if self.decoder_type2=='MixtureNB':
                self.model_omic2=Net_Protein(self.in_dim_2,
                                             protein_back_mean=self.protein_log_back_mean,
                                             protein_back_scale=self.protein_log_back_scale,
                                             decoder_type=self.decoder_type2).to(self.device)
            self.model_omic2=Net_Protein(self.in_dim_2,decoder_type=self.decoder_type2).to(self.device)
            
            self.model_omic3=Net_Image(self.in_dim_3).to(self.device)

        self.optimizer_omic1 = torch.optim.Adam(self.model_omic1.parameters(), self.learning_rate, 
                                          weight_decay=self.weight_decay)
        self.optimizer_omic2 = torch.optim.Adam(self.model_omic2.parameters(), self.learning_rate, 
                                          weight_decay=self.weight_decay)
        
        if self.modality_type=='RNA_Protein_Image':
           self.optimizer_omic3 = torch.optim.Adam(self.model_omic3.parameters(), self.learning_rate, 
                                          weight_decay=self.weight_decay)
 
       
        self.model_omic1.train()
        for epoch in tqdm(range(self.pre_epoch)):
            z1,mu1,logvar1,decoder_reults1=self.model_omic1(self.feature1,self.adj_1)

            kl_1=kl_loss(mu1,logvar1)

            if self.decoder_type1=='ZINB':
                 recon_loss1=ZINBLoss(self.feature1_raw,decoder_reults1[2],decoder_reults1[1],decoder_reults1[0],self.scale_factor1)
            
            if self.decoder_type1=='NB':
                 recon_loss1=NBLoss(self.feature1_raw,decoder_reults1[1],decoder_reults1[0],self.scale_factor1)
            
            if self.decoder_type1=='MSE':
                 recon_loss1=F.mse_loss(self.feature1_normalized,decoder_reults1)
            
            loss1=recon_loss1+0.005*kl_1

            self.optimizer_omic1.zero_grad()
            loss1.backward()
            self.optimizer_omic1.step()
          
          
        Loss2=[]
        self.model_omic2.train()
        if self.modality_type=='RNA and Protein' or self.modality_type=='RNA_Protein_Image':
           for epoch in tqdm(range(self.pre_epoch)):
               z2,mu2,logvar2,decoder_results2=self.model_omic2(self.feature2,self.adj_2)

            
               if self.decoder_type2=='MixtureNB':
                  kl_2=kl_loss(mu2,logvar2)+kl_divergence(decoder_results2[5],decoder_results2[4]).mean()
               else:
                  kl_2=kl_loss(mu2,logvar2)

               if self.decoder_type2=='MixtureNB':
                  recon_loss2=MixtureNBLoss(self.feature2_raw,decoder_results2[0],decoder_results2[1],decoder_results2[2],decoder_results2[3])
               if self.decoder_type2=='NB':
                  recon_loss2=NBLoss(self.feature2_raw,decoder_results2[1],decoder_results2[0],self.scale_factor2)
               if self.decoder_type2=='MSE':
                  recon_loss2=F.mse_loss(self.feature2,decoder_results2)

              
               loss2=recon_loss2+0.005*kl_2

               self.optimizer_omic2.zero_grad()
               loss2.backward()
               self.optimizer_omic2.step()
             
              

        if self.modality_type=='RNA and ATAC':
           for epoch in tqdm(range(self.pre_epoch)):
               z2,mu2,logvar2,decoder_results2=self.model_omic2(self.feature2,self.adj_2)
               kl_2=kl_loss(mu2,logvar2)
               if self.decoder_type2=='ZIP':
                  recon_loss2=ZIPLoss(self.feature2_raw,decoder_results2[0],decoder_results2[1],self.scale_factor2)
               if self.decoder_type2=='Bernoulli':
                  recon_loss2=F.binary_cross_entropy(decoder_results2, self.feature2_binarized)
               if self.decoder_type2=='MSE':
                  recon_loss2=F.mse_loss(self.feature2, decoder_results2)

               loss2=recon_loss2+0.005*kl_2 

               self.optimizer_omic2.zero_grad()
               loss2.backward()
               self.optimizer_omic2.step()
               Loss2.append(loss2.item())
        
        if self.modality_type=='RNA_Protein_Image':
            self.model_omic3.train()
            for epoch in tqdm(range(self.pre_epoch)):
               z3,mu3,logvar3,x_rec3=self.model_omic3(self.feature3,self.adj_3)
               kl_3=kl_loss(mu3,logvar3)
               recon_loss3=F.mse_loss(self.feature3,x_rec3)
               loss3=recon_loss3+0.005*kl_3

               self.optimizer_omic3.zero_grad()
               loss3.backward()
               self.optimizer_omic3.step()
        
   
        #self.model=Net_omic_fusion(self.in_dim_1,self.in_dim_2,self.model_omic1,self.model_omic2,self.modality_type).to(self.device)
        if self.modality_type=='RNA and ATAC':
               self.model=Net_omic_fusion_RNA_ATAC(self.in_dim_1,self.in_dim_2,self.model_omic1,self.model_omic2,
                                                   decoder_type1=self.decoder_type1,decoder_type2=self.decoder_type2).to(self.device)
        if self.modality_type=='RNA and Protein':
               self.model=Net_omic_fusion_RNA_Protein(self.in_dim_1,self.in_dim_2,self.model_omic1,self.model_omic2,
                                                      decoder_type1=self.decoder_type1,decoder_type2=self.decoder_type2).to(self.device)
        if self.modality_type=='RNA_Protein_Image':
               self.model=Net_omic_fusion_RNA_Protein_Image(self.in_dim_1,self.in_dim_2,self.in_dim_3,
                                                            self.model_omic1,self.model_omic2,self.model_omic3,
                                                            decoder_type1=self.decoder_type1,
                                                            decoder_type2=self.decoder_type2
                                                            ).to(self.device)
        
        self.optimizer = torch.optim.Adam(self.model.parameters(), self.learning_rate, 
                                          weight_decay=self.weight_decay)
        

        if self.modality_type=='RNA_Protein_Image':
           self.discriminator=GAN_Discriminator_Tri_modality(self.in_dim_1[2]).to(self.device)
        else:
           self.discriminator=GAN_Discriminator(self.in_dim_1[2]).to(self.device)
           
        self.optimizer_discriminator=torch.optim.RMSprop(self.discriminator.parameters(), lr=self.d_learning_rate)

        d_loss=torch.nn.CrossEntropyLoss(reduce='none')

        D_loss=[]
        G_loss=[]
        self.model.train()
        if self.modality_type=='RNA and Protein':
           for epoch in tqdm(range(self.epoch)):
               #优化判别器
               output,mu1,logvar1,mu2,logvar2=self.model(self.feature1,
                                                     self.feature2,self.adj_1,self.adj_2)
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               label_1=torch.zeros(z1.size(0),dtype=torch.long).to(self.device)
               label_2=torch.ones(z2.size(0),dtype=torch.long).to(self.device)
               label=torch.cat((label_1,label_2),dim=0)
               
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2)),dim=0)
               loss_d=d_loss(pred,label)

               cos_sim = F.cosine_similarity(z1, z2, dim=1)
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights], dim=0)
 
               loss_d=(weights*loss_d).mean()
               
               D_loss.append(loss_d.item())
           
               self.optimizer_discriminator.zero_grad()
               loss_d.backward()
               self.optimizer_discriminator.step()

          
               #优化生成器
               output,mu1,logvar1,mu2,logvar2=self.model(self.feature1,
                                                     self.feature2,self.adj_1,self.adj_2)
               
               if self.decoder_type1=='ZINB':
                 loss1_rec=ZINBLoss(self.feature1_raw,output['decoder_results1'][2],output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='NB':
                 loss1_rec=NBLoss(self.feature1_raw,output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='MSE':
                 loss1_rec=F.mse_loss(self.feature1_normalized,output['decoder_results1'])
 
               if self.decoder_type2=='MixtureNB':
                 loss2_rec=MixtureNBLoss(self.feature2_raw,output['decoder_results2'][0],output['decoder_results2'][1],output['decoder_results2'][2],output['decoder_results2'][3])

               if self.decoder_type2=='NB':
                 loss2_rec=NBLoss(self.feature2_raw,output['decoder_results2'][1],output['decoder_results2'][0],self.scale_factor2)

               if self.decoder_type2=='MSE':
                 loss2_rec=F.mse_loss(self.feature2,output['decoder_results2'])

               kl_1=kl_loss(mu1,logvar1)

               if self.decoder_type2=='MixtureNB':
                   kl_2=kl_loss(mu2,logvar2)+kl_divergence(output['decoder_results2'][5],output['decoder_results2'][4]).mean()
               else:
                   kl_2=kl_loss(mu2,logvar2)
               #计算对抗损失
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2)),dim=0)
               ad_loss=-d_loss(pred,label)

               cos_sim = F.cosine_similarity(z1, z2, dim=1)
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights], dim=0)
               ad_loss=(weights*ad_loss).mean()
               
               loss_recon=self.loss_weight[0]*(loss1_rec)+self.loss_weight[1]*(loss2_rec)+self.loss_weight[2]*(kl_1+kl_2)
               loss=loss_recon+self.ad_weight*ad_loss
   
               self.optimizer.zero_grad()
               loss.backward()
               self.optimizer.step()
      

        if self.modality_type=='RNA and ATAC':
           for epoch in tqdm(range(self.epoch)):
              #优化判别器
               output,mu1,logvar1,mu2,logvar2=self.model(self.feature1,
                                                     self.feature2,self.adj_1,self.adj_2)
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               label_1=torch.zeros(z1.size(0),dtype=torch.long).to(self.device)
               label_2=torch.ones(z2.size(0),dtype=torch.long).to(self.device)
               label=torch.cat((label_1,label_2),dim=0)
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2)),dim=0)
               loss_d=d_loss(pred,label)

               cos_sim = F.cosine_similarity(z1, z2, dim=1)  
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights], dim=0)
 
               loss_d=(weights*loss_d).mean()

               D_loss.append(loss_d.item())

               self.optimizer_discriminator.zero_grad()
               loss_d.backward()
               self.optimizer_discriminator.step()

               
               #优化生成器
               output,mu1,logvar1,mu2,logvar2=self.model(self.feature1,
                                                     self.feature2,self.adj_1,self.adj_2)
               
               if self.decoder_type1=='ZINB':
                 loss1_rec=ZINBLoss(self.feature1_raw,output['decoder_results1'][2],output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='NB':
                 loss1_rec=NBLoss(self.feature1_raw,output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='MSE':
                 loss1_rec=F.mse_loss(self.feature1_normalized,output['decoder_results1'])
 
               if self.decoder_type2=='ZIP':
                 loss2_rec=ZIPLoss(self.feature2_raw,output['decoder_results2'][0],output['decoder_results2'][1],self.scale_factor2)

               if self.decoder_type2=='Bernoulli':
                 loss2_rec=F.binary_cross_entropy(output['decoder_results2'], self.feature2_binarized)
               
               if self.decoder_type2=='MSE':
                 loss2_rec=F.mse_loss(self.feature2,output['decoder_results2'])
               
               
               kl_1=kl_loss(mu1,logvar1)
               kl_2=kl_loss(mu2,logvar2)
               
               #计算对抗损失
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2)),dim=0)
               
               ad_loss=-d_loss(pred,label)

               cos_sim = F.cosine_similarity(z1, z2, dim=1)  
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights], dim=0)

               ad_loss=(weights*ad_loss).mean()
               
               
               loss_recon=self.loss_weight[0]*(loss1_rec)+self.loss_weight[1]*(loss2_rec)+self.loss_weight[2]*(kl_1+kl_2)
               

               loss=loss_recon+self.ad_weight*ad_loss
               

               G_loss.append(loss_recon.item())
            
               self.optimizer.zero_grad()
               loss.backward()
               self.optimizer.step()

    
        if self.modality_type=='RNA_Protein_Image':
           for epoch in tqdm(range(self.epoch)):
              #优化判别器
               output,mu1,logvar1,mu2,logvar2,mu3,logvar3=self.model(self.feature1,
                                                     self.feature2,self.feature3,self.adj_1,self.adj_2,self.adj_3,
                                                     )
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               z3=output['emb_latent_omics3']
               label_1=torch.zeros(z1.size(0),dtype=torch.long).to(self.device)
               label_2=torch.ones(z2.size(0),dtype=torch.long).to(self.device)
               label_3=2*torch.ones(z3.size(0),dtype=torch.long).to(self.device)
               label=torch.cat((label_1,label_2,label_3),dim=0)
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2),self.discriminator(z3)),dim=0)
               loss_d=d_loss(pred,label)
               
               cos_sim = (F.cosine_similarity(z1, z2, dim=1)+F.cosine_similarity(z2, z3, dim=1)+F.cosine_similarity(z1, z3, dim=1))/3
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights,weights], dim=0)

               loss_d=(weights*loss_d).mean()

           
               self.optimizer_discriminator.zero_grad()
               loss_d.backward()
               self.optimizer_discriminator.step()
             
               
               #优化生成器
               output,mu1,logvar1,mu2,logvar2,mu3,logvar3=self.model(self.feature1,
                                                     self.feature2,self.feature3,self.adj_1,self.adj_2,self.adj_3,
                                                     )
               
               if self.decoder_type1=='ZINB':
                 loss1_rec=ZINBLoss(self.feature1_raw,output['decoder_results1'][2],output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='NB':
                 loss1_rec=NBLoss(self.feature1_raw,output['decoder_results1'][1],output['decoder_results1'][0],self.scale_factor1)
            
               if self.decoder_type1=='MSE':
                 loss1_rec=F.mse_loss(self.feature1_normalized,output['decoder_results1'])
 
               if self.decoder_type2=='MixtureNB':
                 loss2_rec=MixtureNBLoss(self.feature2_raw,output['decoder_results2'][0],output['decoder_results2'][1],output['decoder_results2'][2],output['decoder_results2'][3])

               if self.decoder_type2=='NB':
                 loss2_rec=NBLoss(self.feature2_raw,output['decoder_results2'][1],output['decoder_results2'][0],self.scale_factor2)

               if self.decoder_type2=='MSE':
                 loss2_rec=F.mse_loss(self.feature2,output['decoder_results2'])
               
               loss3_rec=F.mse_loss(self.feature3,output['emb_recon_omics3'])

               kl_1=kl_loss(mu1,logvar1)

               if self.decoder_type2=='MixtureNB':
                   kl_2=kl_loss(mu2,logvar2)+kl_divergence(output['decoder_results2'][5],output['decoder_results2'][4]).mean()
               else:
                   kl_2=kl_loss(mu2,logvar2)
               
               kl_3=kl_loss(mu3,logvar3)
               
               z1=output['emb_latent_omics1']
               z2=output['emb_latent_omics2']
               z3=output['emb_latent_omics3']
      
               pred=torch.cat((self.discriminator(z1),self.discriminator(z2),self.discriminator(z3)),dim=0)
               ad_loss=-d_loss(pred,label)

               cos_sim = (F.cosine_similarity(z1, z2, dim=1)+F.cosine_similarity(z2, z3, dim=1)+F.cosine_similarity(z1, z3, dim=1))/3
               weights = F.softmax(cos_sim, dim=0)  
               weights = torch.cat([weights, weights,weights], dim=0)

               ad_loss=(weights*ad_loss).mean()
               
               loss_recon=self.loss_weight[0]*(loss1_rec)+self.loss_weight[1]*(loss2_rec)+self.loss_weight[2]*loss3_rec+self.loss_weight[3]*(kl_1+kl_2+kl_3)
               

               loss=loss_recon+self.ad_weight*ad_loss
               self.optimizer.zero_grad()
               loss.backward()
               self.optimizer.step()

        self.model.eval()
        with torch.no_grad():
            if self.modality_type=='RNA_Protein_Image':
                output,mu1,logvar1,mu2,logvar2,mu3,logvar3=self.model(self.feature1,
                                                     self.feature2,self.feature3,self.adj_1,self.adj_2,self.adj_3,
                                                     )
                z=F.normalize(output['emb_latent_fusion'], p=2, eps=1e-12, dim=1)
            else:
                output,mu1,logvar1,mu2,logvar2=self.model(self.feature1,self.feature2,
                                                    self.adj_1,self.adj_2)  
                z=F.normalize(output['emb_latent_fusion'], p=2, eps=1e-12, dim=1)
         

        self.adata_omic1.obsm['MultiSP']=z.cpu().numpy()

        if self.decoder_type1=='ZINB':
           self.adata_omic1.obsm['denoised_expr']=output['decoder_results1'][2].cpu().numpy()
        if self.decoder_type1=='NB':
           self.adata_omic1.obsm['denoised_expr']=output['decoder_results1'][1].cpu().numpy()
        if self.decoder_type1=='MSE':
           self.adata_omic1.obsm['denoised_expr']=output['decoder_results1'].cpu().numpy()
        
        if self.modality_type=='RNA and Protein':
            if self.decoder_type2=='MixtureNB':
               self.adata_omic2.obsm['denoised_expr']=((1- torch.sigmoid(output['decoder_results2'][2])) * output['decoder_results2'][1]).cpu().numpy()
            
            if self.decoder_type2=='NB':
               self.adata_omic2.obsm['denoised_expr']=output['decoder_results2'][1].cpu().numpy()
            
            if self.decoder_type2=='MSE':
               self.adata_omic2.obsm['denoised_expr']=output['decoder_results2'].cpu().numpy()


        if self.modality_type=='RNA and ATAC':
            if self.decoder_type2=='ZIP':
               self.adata_omic2.obsm['denoised_expr']=output['decoder_results2'][1].cpu().numpy()
            if self.decoder_type2=='Bernoulli':
               self.adata_omic2.obsm['denoised_expr']=output['decoder_results2'].cpu().numpy()
    
        return self.adata_omic1,self.adata_omic2