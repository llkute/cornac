# -*- coding: utf-8 -*-
"""
@author: Aghiles Salah <asalah@smu.edu.sg>
"""



import numpy as np
from ..recommender import Recommender
from .pcrl import Pcrl_

#Recommender class for Probabilistic Collaborative Representation Learning (PCRL)
class Pcrl(Recommender):
    """Probabilistic Collaborative Representation Learning.

    Parameters
    ----------
    k: int, optional, default: 100
        The dimension of the latent factors.
        
    z_dims: Numpy 1d array, optional, default: [300]
        The dimensions of the hidden intermdiate layers 'z' in the order \
        [dim(z_L), ...,dim(z_1)], please refer to Figure 1 in the orginal paper for more details.

    max_iter: int, optional, default: 300
        Maximum number of iterations (number of epochs) for variational PCRL.
        
    batch_size: int, optional, default: 300
        The batch size for SGD.
        
    learning_rate: float, optional, default: 0.001
        The learning rate for SGD.

    aux_info: csc sparse matrix, required
        The item auxiliary information matrix, item-context in the PCRL's paper, \
        in the scipy csc sparse format.

    name: string, optional, default: 'PCRL'
        The name of the recommender model.

    trainable: boolean, optional, default: True
        When False, the model is not trained and Cornac assumes that the model already \
        pre-trained (Theta, Beta and Xi are not None). 
        
    w_determinist: boolean, optional, default: True
        When True, determinist wheights "W" are used for the generator network, \
        otherwise "W" is stochastic as in the original paper.

    init_params: dictionary, optional, default: None
        List of initial parameters, e.g., init_params = {'G_s':G_s, 'G_r':G_r, 'L_s':L_s, 'L_r':L_r}, \
        where G_s and G_r are of type csc_matrix or np.array with the same shape as Theta, see below). \
        They represent respectively the "shape" and "rate" parameters of Gamma distribution over \
        Theta. It is the same for L_s, L_r and Beta.

    Theta: csc_matrix, shape (n_users,k)
        The expected user latent factors.

    Beta: csc_matrix, shape (n_items,k)
        The expected item latent factors.

    References
    ----------
    * Salah, Aghiles, and Hady W. Lauw. Probabilistic Collaborative Representation Learning for Personalized Item Recommendation. \
    In UAI 2018.
    """    

    def __init__(self, k=100, z_dims = [300], max_iter=300, batch_size = 300,learning_rate = 0.001,aux_info = None, name = "pcrl", trainable = True,w_determinist = True, init_params = None):

        Recommender.__init__(self, name=name, trainable = trainable)

        self.aux_info = aux_info 
        self.k = k
        self.z_dims = z_dims                #the dimension of the second hidden layer (we consider a 2-layers PCRL)
        self.max_iter = max_iter
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.init_params = init_params
        self.w_determinist = w_determinist

        
        
    #fit the recommender model to the traning data    
    def fit(self,X):
        """Fit the model to observations.

        Parameters
        ----------
        X: scipy sparse matrix, required
            the user-item preference matrix (traning data), in a scipy sparse format\
            (e.g., csc_matrix).
        """
        if self.trainable:
            #intanciate pcrl
            pcrl_ = Pcrl_(cf_data = X, aux_data = self.aux_info, k =self.k,z_dims = self.z_dims, n_epoch=self.max_iter,batch_size = self.batch_size,learning_rate = self.learning_rate, B = 1,w_determinist = self.w_determinist, init_params = self.init_params)
            pcrl_.learn()
                        
            self.Theta = np.array(pcrl_.Gs)/np.array(pcrl_.Gr)
            self.Beta = np.array(pcrl_.Ls)/np.array(pcrl_.Lr)
        else:
            print('%s is trained already (trainable = False)' % (self.name))
        
   
    

    #get prefiction for a single user (predictions for one user at a time for efficiency purposes)
    #predictions are not stored for the same efficiency reasons        
    def predict(self,index_user):
        """Predic the scores (ratings) of a user for all items.

        Parameters
        ----------
        index_user: int, required
            The index of the user for whom to perform predictions.

        Returns
        -------
        Numpy 1d array 
            Array containing the predicted values for all items
        """
        
        user_pred = self.Beta*self.Theta[index_user,:].T
        #transform user_pred to a flatten array, but keep thinking about another possible format
        user_pred = np.array(user_pred,dtype='float64').flatten()
        
        return user_pred
        
        