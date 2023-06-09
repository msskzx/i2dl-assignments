"""Models for facial keypoint detection"""

import torch
import torch.nn as nn

class KeypointModel(nn.Module):
    """Facial keypoint detection model"""
    def __init__(self, hparams):
        """
        Initialize your model from a given dict containing all your hparams
        Warning: Don't change the method declaration (i.e. by adding more
            arguments), otherwise it might not work on the submission server
            
        """
        super().__init__()
        self.hparams = hparams      
        
        ########################################################################
        # TODO: Define all the layers of your CNN, the only requirements are:  #
        # 1. The network takes in a batch of images of shape (Nx1x96x96)       #
        # 2. It ends with a linear layer that represents the keypoints.        #
        # Thus, the output layer needs to have shape (Nx30),                   #
        # with 2 values representing each of the 15 keypoint (x, y) pairs      #
        #                                                                      #
        # Some layers you might consider including:                            #
        # maxpooling layers, multiple conv layers, fully-connected layers,     #
        # and other layers (such as dropout or batch normalization) to avoid   #
        # overfitting.                                                         #
        #                                                                      #
        # We would truly recommend to make your code generic, such as you      #
        # automate the calculation of the number of parameters at each layer.  #
        # You're going probably try different architecutres, and that will     #
        # allow you to be quick and flexible.                                  #
        ########################################################################

        def conv_group(input_channels, output_channels, dropout):
            conv = nn.Conv2d(input_channels, output_channels, kernel_size=self.hparams['kernel_size'],
                      stride=self.hparams['stride'], padding=self.hparams['padding'])
            nn.init.kaiming_normal_(conv.weight, nonlinearity='relu')

            return nn.Sequential(
                conv,
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=self.hparams['maxpool_kernel_size'], stride=self.hparams['maxpool_stride']),
                nn.Dropout(p=dropout)
            )
        
        num_conv_layers = 4
        layers = []
        input_channels = self.hparams['in_channels']
        output_channels = self.hparams['out_channels']
        final_image_size = self.hparams['input_size']

        for i in range(num_conv_layers):
            layers.append(conv_group(input_channels, output_channels, self.hparams['dropout'] + (i * 0.1)))
            input_channels = output_channels
            output_channels *= 2
            # calculate final image size
            final_image_size = int((final_image_size - self.hparams['kernel_size'] + 2 * self.hparams['padding']) / self.hparams['stride']) + 1
            final_image_size = int((final_image_size - self.hparams['maxpool_kernel_size']) / self.hparams['maxpool_stride']) + 1

        self.features = nn.Sequential(*layers)

        # fully connected layers
        self.fc1 = nn.Sequential(nn.Linear(self.hparams['out_channels'] * 8 * final_image_size * final_image_size, self.hparams['out_channels'] * 8), nn.ReLU())
        nn.init.kaiming_normal_(self.fc1[0].weight, nonlinearity='relu')
        
        self.fc2 = nn.Sequential(nn.Linear(self.hparams['out_channels'] * 8, self.hparams['num_keypoints']))
        nn.init.xavier_normal_(self.fc2[0].weight)

        ########################################################################
        #                           END OF YOUR CODE                           #
        ########################################################################

    def forward(self, x):
        
        # check dimensions to use show_keypoint_predictions later
        if x.dim() == 3:
            x = torch.unsqueeze(x, 0)
        ########################################################################
        # TODO: Define the forward pass behavior of your model                 #
        # for an input image x, forward(x) should return the                   #
        # corresponding predicted keypoints.                                   #
        # NOTE: what is the required output size?                              #
        ########################################################################

        # extract features
        x = self.features(x)
        # flatten
        x = x.view(x.size(0), -1)
        # fully connected layer
        x = self.fc1(x)
        x = self.fc2(x)

        ########################################################################
        #                           END OF YOUR CODE                           #
        ########################################################################
        return x
    
class DummyKeypointModel(nn.Module):
    """Dummy model always predicting the keypoints of the first train sample"""
    def __init__(self):
        super().__init__()
        self.prediction = torch.tensor([[
            0.4685, -0.2319,
            -0.4253, -0.1953,
            0.2908, -0.2214,
            0.5992, -0.2214,
            -0.2685, -0.2109,
            -0.5873, -0.1900,
            0.1967, -0.3827,
            0.7656, -0.4295,
            -0.2035, -0.3758,
            -0.7389, -0.3573,
            0.0086, 0.2333,
            0.4163, 0.6620,
            -0.3521, 0.6985,
            0.0138, 0.6045,
            0.0190, 0.9076,
        ]])

    def forward(self, x):
        return self.prediction.repeat(x.size()[0], 1, 1, 1)
