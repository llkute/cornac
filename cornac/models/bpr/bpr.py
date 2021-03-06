# -*- coding: utf-8 -*-
"""
@author: Guo Jingyao
"""


import numpy as np
import random
import torch
from torch.utils.data import DataLoader




"""Generate training data pairs:
   given rated item i, randomly choose item j and check whether rating of j is missing or lower than i, 
   if not randomly sample another item. 
   each row of the sampled data in the following form:
   [userId itemId_i itemId_j rating_i rating_j]
   for each user u, he/she prefers item i over item j.
   """
def sampleData(X, data):
    X = X.todense()
    sampled_data = np.zeros((data.shape[0], 5), dtype=np.int)
    data = data.astype(int)

    for k in range(0, data.shape[0]):
        u = data[k, 0]
        i = data[k, 1]
        ratingi = data[k, 2]
        j = random.randint(0, X.shape[0])

        while X[u, j] > ratingi:
            j = random.randint(0, data.shape[1])

        sampled_data[k, :] = [u, i, j, ratingi, X[u, j]]

    return sampled_data


	
	
	
def bpr(X, data, k, lamda = 0.01, n_epochs=100, learning_rate=0.001,batch_size = 100, init_params=None):

    #Initial user factors
    if init_params['U'] is None:
        U = torch.randn(X.shape[0], k, requires_grad=True)
    else:
        U = init_params['U']

    #Initial item factors
    if init_params['V'] is None:
        V = torch.randn(X.shape[1], k, requires_grad=True)
    else:
        V = init_params['V']

    optimizer = torch.optim.Adam([U, V], lr=learning_rate)
    for epoch in range(n_epochs):
        # for each epoch, randomly sample training pair
        Data = sampleData(X, data)
        # set batch size for each step, and shuffle the training data
        train_loader = torch.utils.data.DataLoader(Data, batch_size=batch_size, shuffle=True)
        for step, batch_data in enumerate(train_loader):
            R = U.mm(V.t())
            batch_data = np.array(batch_data)
            regU = U[batch_data[:, 0], :]
            regV = V[np.unique(np.append(batch_data[:, 1], batch_data[:, 2])), :]

            Ratingi = R[batch_data[:, 0], batch_data[:, 1]]
            Ratingj = R[batch_data[:, 0], batch_data[:, 2]]

            loss = lamda * (torch.trace(regU.mm(regU.t())) + torch.trace(regV.mm(regV.t()))) - torch.log(
                torch.sigmoid(Ratingi.add(Ratingj * -1))).sum()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print('epoch:',epoch,'loss:', loss)

    U = U.data.numpy()
    V = V.data.numpy()

    res = {'U': U, 'V': V}

    return res