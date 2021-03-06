import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
# from .base_model import BaseModel
from torch_stft import STFT
# import matplotlib.pyplot as plt
from data_loader.data_loaders import get_unified_feature




def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)

class SELayer(nn.Module):
    def __init__(self, channel, reduction=16):
        super(SELayer, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1) # F_squeeze 
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        # print(y.shape)
        # print(y)
        return x * y.expand_as(x)

class  Resolution_ attention(nn.Module):
    def __init__(self, channel, reduction=3):
        super(SELayer1, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1) # F_squeeze
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        y = y.view(b, c, 1, 1)
        # The index of the resolution is sorted according to the contribution value
        if eval:
            k = y.view(b, c).cpu().data.numpy()
            sum_col_list1 = []
            for i in range(len(k[0])):
                count = 0
                for j in range(len(k)):
                    count += k[j][i]
                # count = count//len(k[1])
                sum_col_list1.append(count)
             
            Indexes = sorted(range(len(sum_col_list1)), key=lambda k: sum_col_list1[k])
            sum_col_list1.sort()
            time_gap_list = [sum_col_list1[i + 1] - sum_col_list1[i] for i in range(len(sum_col_list1) - 1)]
            m  = sorted(range(len(time_gap_list)), key=lambda k: time_gap_list[k])
            m=m[-1]+1
            HighContribution=Indexes[m:]
        return x * y.expand_as(x)

class SEBasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None, reduction=16):
        super(SEBasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes, 1)
        self.bn2 = nn.BatchNorm2d(planes)
        self.se = SELayer(planes, reduction)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out = self.se(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out
class SEBottleneck(nn.Module):
    expansion = 2

    def __init__(self, inplanes, planes, stride=1, downsample=None, reduction=16):
        super(SEBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * self.expansion, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.se = SELayer(planes * self.expansion, reduction)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)
        out = self.se(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

class ResNet(nn.Module):
    """ basic ResNet class: https://github.com/pytorch/vision/blob/master/torchvision/models/resnet.py """
    def __init__(self, block, layers,  screen, High_contribution=[],Full=[],resolution=13,channels=[16, 16, 32, 64, 128], num_classes=2, focal_loss=False):
        
        self.inplanes = channels[0]
        self.focal_loss = focal_loss 
        self.resolution= resolution
        self.High_contribution= High_contribution
        self.screen=screen
        self.full=Full
        super(ResNet, self).__init__()
        
        self.stft = self._prepare_network(window='blackman')#Online feature extraction
        #Resolution weight attention
        if screen:
            self.Resolution_ attention = Resolution_ attention(channel=resolution, reduction=resolution//2)
        
        self.conv1 = nn.Conv2d(resolution, channels[0], kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(channels[0])
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(block, channels[1], layers[0])
        self.layer2 = self._make_layer(block, channels[2], layers[1], stride=2)
        self.layer3 = self._make_layer(block, channels[3], layers[2], stride=2)
        self.layer4 = self._make_layer(block, channels[4], layers[3], stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1)) 

        self.classifier = nn.Linear(channels[4] * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def _make_layer(self, block,  planes , blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def __str__(self):
        """
        Model prints with number of trainable parameters
        """
        model_parameters = filter(lambda p: p.requires_grad, self.parameters())
        params = sum([np.prod(p.size()) for p in model_parameters])
        return super(ResNet, self).__str__() + '\nTrainable parameters: {}'.format(params)

    def _prepare_network(self,  window='blackman'):
        
        parameter =self.full
        stft =[]
        if self.screen:
            llen = len(parameter)
            for i in range(0, llen):
                fft = STFT(
                    filter_length=parameter[i][0],

                    hop_length=parameter[i][1],
                    win_length=parameter[i][0],
                    window=window
                )
                stft.append(fft)
        else:
            llen = len(self.High_contribution)
            for i in range(0, llen):
                j = self.High_contribution[i]
                fft = STFT(
                    filter_length=parameter[j][0],

                    hop_length=parameter[j][1],
                    win_length=parameter[j][0],
                    window=window
                )
                stft.append(fft)
        return stft

    def forward(self, x, eval=False):

       m = nn.AdaptiveMaxPool2d((1218, 1025))
        k = []
        for i in range(0,n):
            y, _ = self.stft[i].transform(x)
            y = y.permute(0, 2, 1).unsqueeze(1)
            y =m(y)
            k.append(y)

        x = torch.cat(k, 1)
        # print(x1.size())
        if self.screen:
            x = self.Resolution_ attention(x)
        # print(x1)
        x = self.conv1(x)
        # print(x.size())
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        #print(x.size())

        x = self.layer1(x)
        #print(x.size())
        x = self.layer2(x)
        #print(x.size())
        x = self.layer3(x)
        #print(x.size())
        x = self.layer4(x)
        #print(x.size())

        x = self.avgpool(x).view(x.size()[0], -1)
        #print(x.shape)
        out = self.classifier(x)
        # print(out.shape)

        # if self.focal_loss: return out 
        if not eval:
            return (F.log_softmax(out, dim=-1), None)
        else:
            return F.log_softmax(out, dim=-1)

# class SEResNet34(BaseModel):
#     def __init__(self, layers=[3, 4, 6, 3], num_classes=2, focal_loss=False):
#         super(SEResNet34, self).__init__()
#         self.resnet =  ResNet(SEBasicBlock, layers=layers, num_classes=num_classes, focal_loss=focal_loss)

#     def forward(self, x):
#         return self.resnet(x)

def se_resnet34(**kwargs):
    model = ResNet(SEBasicBlock, [3, 4, 6, 3], **kwargs)
    return model

def se_resnet12(**kwargs):
    model = ResNet(SEBasicBlock, [1, 2, 3, 1], **kwargs)
    return model

def se_resnet50(**kwargs):
    model = ResNet(SEBottleneck, [3, 4, 6, 3], **kwargs)
    return model

if __name__=='__main__':
    a = torch.rand(64, 1200)
    model = se_resnet34()
    b = model(a)
    print(b)

