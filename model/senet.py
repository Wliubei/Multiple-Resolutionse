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

class SELayer1(nn.Module):
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
        # k = y.view(b, c).cpu().data.numpy()
        # plt.figure(figsize=(6, 6))
        # plt.subplot(211)
        # plt.title('Contribution of different resolutions to the model')
        # plt.xlabel('resolutions')
        # plt.ylabel('batch_size')
        # plt.imshow(k, aspect='auto', origin='lower', cmap="YlGnBu_r")
        # plt.savefig('resolutions.png')
        # plt.show()
        # plt.plot(np.sort(np.sum(k,axis=0)))
        # plt.show()
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
    def __init__(self, block, layers, channels=[16, 16, 32, 64, 128], num_classes=2, focal_loss=False):
        
        self.inplanes = channels[0]
        self.focal_loss = focal_loss 

        super(ResNet, self).__init__()
        self.stft = self._prepare_network(window='blackman')
        
        self.se1 = SELayer1(channel=7, reduction=7)#权重
        self.conv1 = nn.Conv2d(7, channels[0], kernel_size=7, stride=2, padding=3, bias=False)
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
        # parameter = [(512, 128), (1024, 256),(1724, 130)]#lazixian
        # parameter = [(1724, 130), (2048, 512)]#lazhigao34

        # parameter = [(512, 64), (512, 128), (1724, 130)]pa 11
        # parameter = [(288, 96), (400, 160), (480, 120), (512, 64), (512, 128), (1024, 64), (1024, 128), (1024, 256),  (2048, 128), (2048, 256), (1724, 130), (2048, 512), (2048, 64)]#pa50,13
        # parameter = [(480, 120), (1024, 64), (2048, 64)]#$plxuan
        # parameter = [ (1024, 128), (2048, 128), (2048, 256)]#PAZHIGAO
        parameter = [(128,32),(256,64), (400, 160),(512, 64), (512, 128), (1024, 64), (1024, 128), (1024, 256), (2048, 128), (2048, 256), (1724, 130),
                     (2048, 512), (2048, 64)]
        # parameter = [(400, 160), (512, 64), (512, 128), (1024, 64), (1024, 128), (1024, 256),
        #               (2048, 128),  (2048, 512),(1724, 130),(2048, 64)]
        # stft1 = STFT(
        #     filter_length=parameter[0][0],
        #
        #     hop_length=parameter[0][1],
        #     win_length=parameter[0][0],
        #     window=window
        # )
        # stft2 = STFT(
        #     filter_length=parameter[1][0],
        #
        #     hop_length=parameter[1][1],
        #     win_length=parameter[1][0],
        #     window=window
        # )
        # stft3 = STFT(
        #     filter_length=parameter[2][0],
        #
        #     hop_length=parameter[2][1],
        #     win_length=parameter[2][0],
        #     window=window
        # )
        stft4 = STFT(
            filter_length=parameter[3][0],

            hop_length=parameter[3][1],
            win_length=parameter[3][0],
            window=window
        )
        stft5 = STFT(
            filter_length=parameter[4][0],

            hop_length=parameter[4][1],
            win_length=parameter[4][0],
            window=window
        )
        # stft6 = STFT(
        #     filter_length=parameter[5][0],
        #
        #     hop_length=parameter[5][1],
        #     win_length=parameter[5][0],
        #     window=window
        # )
        stft7 = STFT(
            filter_length=parameter[6][0],

            hop_length=parameter[6][1],
            win_length=parameter[6][0],
            window=window
        )
        stft8 = STFT(
            filter_length=parameter[7][0],

            hop_length=parameter[7][1],
            win_length=parameter[7][0],
            window=window
        )
        # stft9 = STFT(
        #     filter_length=parameter[8][0],
        #
        #     hop_length=parameter[8][1],
        #     win_length=parameter[8][0],
        #     window=window
        # )
        # stft10 = STFT(
        #     filter_length=parameter[9][0],
        #
        #     hop_length=parameter[9][1],
        #     win_length=parameter[9][0],
        #     window=window
        # )
        stft11 = STFT(
            filter_length=parameter[10][0],

            hop_length=parameter[10][1],
            win_length=parameter[10][0],
            window=window
        )
        stft12 = STFT(
            filter_length=parameter[11][0],

            hop_length=parameter[11][1],
            win_length=parameter[11][0],
            window=window
        )
        stft13 = STFT(
            filter_length=parameter[12][0],

            hop_length=parameter[12][1],
            win_length=parameter[12][0],
            window=window
        )

        # print(parameter[0][0])
        # return stft1, stft2, stft3, stft4, stft5, stft6, stft7, stft8, stft9, stft10,stft11,stft12,stft13
        return stft4, stft5,stft7,stft8,stft11,stft12,stft13
    def forward(self, x, eval=False):
        #print(x.size())

        x1,_ = self.stft[0].transform(x)
        x2, _ = self.stft[1].transform(x)
        x3, _ = self.stft[2].transform(x)
        x4, _ = self.stft[3].transform(x)
        x5, _ = self.stft[4].transform(x)
        x6, _ = self.stft[5].transform(x)
        x7, _ = self.stft[6].transform(x)
        # x8, _ = self.stft[7].transform(x)
        # x9, _ = self.stft[8].transform(x)
        # x10, _ = self.stft[9].transform(x)
        # x11, _ = self.stft[10].transform(x)
        # x12, _ = self.stft[11].transform(x)
        # x13, _ = self.stft[12].transform(x)


        x1 = x1.permute(0, 2, 1).unsqueeze(1)
        x2 = x2.permute(0, 2, 1).unsqueeze(1)
        # print(x2.size())
        x3 = x3.permute(0, 2, 1).unsqueeze(1)
        x4 = x4.permute(0, 2, 1).unsqueeze(1)
        x5 = x5.permute(0, 2, 1).unsqueeze(1)
        x6 = x6.permute(0, 2, 1).unsqueeze(1)
        x7 = x7.permute(0, 2, 1).unsqueeze(1)
        # x8 = x8.permute(0, 2, 1).unsqueeze(1)
        # x9 = x9.permute(0, 2, 1).unsqueeze(1)
        # x10 = x10.permute(0, 2, 1).unsqueeze(1)
        # x11 = x11.permute(0, 2, 1).unsqueeze(1)
        # x12 = x12.permute(0, 2, 1).unsqueeze(1)
        # x13 = x13.permute(0, 2, 1).unsqueeze(1)

        # print(x11.size())
        # m= nn.Upsample()
        m= nn.AdaptiveMaxPool2d((1218, 1025))
        x1 = m(x1)
        x2 = m(x2)
        x3 = m(x3)
        x4 = m(x4)
        x5 = m(x5)
        x6 = m(x6)
        # x7 = m(x7)
        # x8 = m(x8)
        # x9 = m(x9)
        # x10 = m(x10)
        # x11 = m(x11)
        # x12 = m(x12)

        # x1= torch.cat((x1, x2, x3, x4, x5, x6, x7, x8, x9, x10,x11,x12,x13), 1)
        x1 = torch.cat((x1, x2, x3, x4, x5, x6, x7), 1)
        # print(x1.size())
        x = self.se1(x1)
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
