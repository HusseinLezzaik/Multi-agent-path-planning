"""
Code for building and training MLP decentralized model for Robots from Fully Connected Graph
Data Collected from running a Fully Connected Graph
Deeper GNN Network
*Input: Mx, My, Phix, Phiy
*Output: Ux, Uy
"""

# PyTorch MLP for Regression
from numpy import vstack
from numpy import sqrt
from pandas import read_csv
from sklearn.metrics import mean_squared_error
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torch import Tensor
from torch.nn import Linear
from torch.nn import ReLU
from torch.nn import Module
from torch.optim import SGD
from torch.nn import MSELoss
from torch.nn.init import xavier_uniform_

# dataset definition
class CSVDataset(Dataset):
    # load the dataset
    def __init__(self, path):
        # load the csv file as a dataframe
        df = read_csv(path, header=None)
        # store the inputs and outputs
        self.X = df.values[:, :4].astype('float32') # read first 4 values
        self.M = df.values[:, :2].astype('float32') # read first two values
        self.Phi = df.values[:, 2:4].astype('float32') # read 3rd/4th values
        self.y = df.values[:, 4:].astype('float32') # read last two values
        # ensure target has the right shape
        self.y = self.y.reshape((len(self.y), 2)) # nx2

    # number of rows in the dataset
    def __len__(self):
        return len(self.X)

    # get a row at an index
    def __getitem__(self, idx):
        return [self.X[idx], self.y[idx]]

    # get indexes for train and test rows
    def get_splits(self, n_test=0.3):
        # determine sizes
        test_size = round(n_test * len(self.X))
        train_size = len(self.X) - test_size
        # calculate the split
        return random_split(self, [train_size, test_size])

# model definition
class ModelA(Module):
    # define model elements
    def __init__(self):
        super(ModelA, self).__init__()
        # Inputs to hidden layer linear transformation
        self.input = Linear(2, 3) # 2 inputs, 3 hidden units
        xavier_uniform_(self.input.weight)
        self.act1 = ReLU()
        # Define Hidden Layer
        self.hidden1 = Linear(3, 3)
        xavier_uniform_(self.hidden1.weight)
        self.act2 = ReLU() 
        # Output Layer 3 to 2 units
        self.output = Linear(3, 2)
        xavier_uniform_(self.output.weight)

    # forward propagate input
    def forward(self, M):
        # Pass the input tensor through each of our operations
        # Input to first hidden layer
        X = self.input(M)
        X = self.act1(M)
        # Second hidden layer
        X = self.hidden1(M)
        X = self.act2(M)
        # Final hidden layer and Output
        X = self.output(M)
        return X

class ModelB(Module):
    # define model elements
    def __init__(self):
        super(ModelB, self).__init__()
        # Inputs to hidden layer linear transformation
        self.input = Linear(2, 3) # 2 inputs, 3 hidden units
        xavier_uniform_(self.input.weight)
        self.act1 = ReLU()
        # Define Hidden Layer
        self.hidden1 = Linear(3, 3)
        xavier_uniform_(self.hidden1.weight)
        self.act2 = ReLU() 
        # Output layer 3 to 2 units
        self.output = Linear(3, 2)
        xavier_uniform_(self.output.weight)

    # forward propagate input
    def forward(self, Phi):
        # Pass the input tensor through each of our operations
        # Input to first hidden layer
        X = self.input(Phi)
        X = self.act1(Phi)
        # Second hidden layer
        X = self.hidden1(Phi)
        X = self.act2(Phi)
        # Final hidden layer and Output
        X = self.output(Phi)
        return X

class ModelE(Module):
    # define model elements
    def __init__(self, ModelA, ModelB):
        super(ModelE, self).__init__()
        self.modelA = ModelA
        self.modelB = ModelB
        # Define 4x3 hidden unit
        self.hidden = Linear(4,3)
        xavier_uniform_(self.hidden.weight)
        self.act1 = ReLU()
        # Define Output 3x2 unit        
        self.output = Linear(3,2)
        xavier_uniform_(self.output.weight)

    # forward propagate input
    def forward(self, M, Phi):
        # Pass the input tensor through each of our operations
        # Input to first hidden layer
        x1 = self.modelA(M)
        x2 = self.modelB(Phi)
        # Combine Models
        X = torch.cat((x1, x2), dim=1)
        # Define Hidden Layer
        X = self.hidden(X)
        X = self.act1(X)
        # Output Layer
        X = self.output(X)
        return X

# prepare the dataset
def prepare_data(path):
    # load the dataset
    dataset = CSVDataset(path)
    # calculate split
    train, test = dataset.get_splits()
    # prepare data loaders
    train_dl = DataLoader(train, batch_size=32, shuffle=True)
    test_dl = DataLoader(test, batch_size=1024, shuffle=False)
    return train_dl, test_dl

# train the model
def train_model(train_dl, model):
    # define the optimization
    criterion = MSELoss()
    optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9)
    # enumerate epochs
    for epoch in range(150):
        # enumerate mini batches
        for i, (inputs, targets) in enumerate(train_dl):
            # clear the gradients
            optimizer.zero_grad()
            # compute the model output
            yhat = model(inputs)
            # calculate loss
            loss = criterion(yhat, targets)
            # credit assignment
            loss.backward()
            # update model weights
            optimizer.step()

# evaluate the model
def evaluate_model(test_dl, model):
    predictions, actuals = list(), list()
    for i, (inputs, targets) in enumerate(test_dl):
        # evaluate the model on the test set
        yhat = model(inputs)
        # retrieve numpy array
        yhat = yhat.detach().numpy()
        actual = targets.numpy()
        actual = actual.reshape((len(actual), 2))
        # store
        predictions.append(yhat)
        actuals.append(actual)
    predictions, actuals = vstack(predictions), vstack(actuals)
    print(predictions)
    # calculate mse
    mse = mean_squared_error(actuals, predictions)
    return mse

# make a class prediction for one row of data
def predict(row, model):
    # convert row to data
    row = Tensor([row])
    # make prediction
    yhat = model(row)
    # retrieve numpy array
    yhat = yhat.detach().numpy()
    return yhat

# prepare the data
path = '/home/hussein/Desktop/Multi-agent-path-planning/Real Topology  Graph/GNN Model 4/Fully Connected Graph/43k_dataset.csv'

train_dl, test_dl = prepare_data(path)

print(len(train_dl.dataset), len(test_dl.dataset))

# define the network
modelA = ModelA()
modelB = ModelB()
model = ModelE(modelA, modelB)

# train the model
train_model(train_dl, model)

# evaluate the model
mse = evaluate_model(test_dl, model)
print('MSE: %.3f, RMSE: %.3f' % (mse, sqrt(mse)))


# save model using dict
FILE = "model.pth"
torch.save(model.state_dict(), FILE)