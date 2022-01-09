import sys, os
import argparse
import collections
import torch
import numpy as np
import data_loader.data_loaders as module_data
import model.loss as module_loss
import model.metric as module_metric
import model as module_arch
from parse_config import ConfigParser
from trainer import Trainer

torch.manual_seed(2019)  #cpu
torch.cuda.manual_seed(2019) #gpu
np.random.seed(2019) #numpy
# random.seed(1234) #random and transforms
class ScheduledOptim(object):
    """ A simple wrapper class for learning rate scheduling """

    def __init__(self, optimizer, n_warmup_steps):
        self.optimizer = optimizer
        self.d_model = 64
        self.n_warmup_steps = n_warmup_steps
        self.n_current_steps = 0
        self.delta = 1

    def step(self):
        "Step by the inner optimizer"
        self.optimizer.step()

    def zero_grad(self):
        "Zero out the gradients by the inner optimizer"
        self.optimizer.zero_grad()

    def increase_delta(self):
        self.delta *= 2

    def update_learning_rate(self):
        "Learning rate scheduling per step"

        self.n_current_steps += self.delta
        new_lr = np.power(self.d_model, -0.5) * np.min([
            np.power(self.n_current_steps, -0.5),
            np.power(self.n_warmup_steps, -1.5) * self.n_current_steps])

        for param_group in self.optimizer.param_groups:
            param_group['lr'] = new_lr
        return new_lr

    def state_dict(self):
        ret = {
            'd_model': self.d_model,
            'n_warmup_steps': self.n_warmup_steps,
            'n_current_steps': self.n_current_steps,
            'delta': self.delta,
        }
        ret['optimizer'] = self.optimizer.state_dict()
        return ret

    def load_state_dict(self, state_dict):
        self.d_model = state_dict['d_model']
        self.n_warmup_steps = state_dict['n_warmup_steps']
        self.n_current_steps = state_dict['n_current_steps']
        self.delta = state_dict['delta']
        self.optimizer.load_state_dict(state_dict['optimizer'])


def main(config):
    logger = config.get_logger('train')

    # setup data_loader instances
    data_loader = config.initialize('train_data_loader', module_data)
    valid_data_loader = config.initialize('dev_data_loader', module_data)   #data_loader.split_validation()

    # build model architecture, then print to console
    model = config.initialize('arch', module_arch)
    # logger.info(model)

    # get function handles of loss and metrics
    loss = config.initialize('loss', module_loss)
    # loss = getattr(module_loss, config['loss'])
    metrics = [getattr(module_metric, met) for met in config['metrics']]

    # build optimizer, learning rate scheduler. delete every lines containing lr_scheduler for disabling scheduler
    trainable_params = filter(lambda p: p.requires_grad, model.parameters())
    # optimizer = config.initialize('optimizer', torch.optim, trainable_params)
    n_warmup_steps=1000
    optimizer = ScheduledOptim(
        torch.optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            betas=(0.9, 0.98), eps=1e-09, weight_decay=1e-9, amsgrad=True),
        n_warmup_steps)
    if config['lr_scheduler'] is not None:
        lr_scheduler = config.initialize('lr_scheduler', torch.optim.lr_scheduler, optimizer)
    else:
        lr_scheduler = None
        
    trainer = Trainer(model, loss, metrics, optimizer,
                      config=config,
                      data_loader=data_loader,
                      valid_data_loader=valid_data_loader,
                      lr_scheduler=lr_scheduler)

    trainer.train()


if __name__ == '__main__':
    args = argparse.ArgumentParser(description='ASVSpoof2019 project')
    args.add_argument('-c', '--config', default=None, type=str,
                        help='config file path (default: None)')
    args.add_argument('-r', '--resume', default=None, type=str,
                        help='path to latest checkpoint (default: None)')
    args.add_argument('-d', '--device', default=None, type=str,
                        help='indices of GPUs to enable (default: all)')

    # custom cli options to modify configuration from default values given in json file.
    CustomArgs = collections.namedtuple('CustomArgs', 'flags type target')
    options = [
        CustomArgs(['--lr', '--learning_rate'], type=float, target=('optimizer', 'args', 'lr')),
        CustomArgs(['--bstrn', '--batch_size_trn'], type=int, target=('train_data_loader', 'args', 'batch_size')),
        CustomArgs(['--bsdev', '--batch_size_dev'], type=int, target=('dev_data_loader', 'args', 'batch_size'))
    ]
    config = ConfigParser(args, options)
    main(config)
