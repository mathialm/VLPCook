import torch
import torch.nn as nn
from bootstrap.lib.logger import Logger
from bootstrap.lib.options import Options
from .triplet import Triplet
from .pairwise import Pairwise
from .vlp_triplet import VLPTriplet 


class Trijoint(nn.Module):

    def __init__(self, opt, nb_classes, dim_emb, with_classif=False, engine=None):
        super(Trijoint, self).__init__()


        self.with_classif = with_classif
        if self.with_classif:
            self.weight_classif = opt['weight_classif']
            if self.weight_classif == 0:
                Logger()('You should use "--model.with_classif False"', Logger.ERROR)
            self.weight_retrieval = 1 - 2 * opt['weight_classif']

        self.keep_background = opt.get('keep_background', False)
        if self.keep_background:
            # http://pytorch.org/docs/master/nn.html?highlight=crossentropy#torch.nn.CrossEntropyLoss
            self.ignore_index = -100
        else:
            self.ignore_index = 0

        Logger()('ignore_index={}'.format(self.ignore_index))
        if self.with_classif:
            self.criterion_image_classif = nn.CrossEntropyLoss(ignore_index=self.ignore_index)
            self.criterion_recipe_classif = nn.CrossEntropyLoss(ignore_index=self.ignore_index)

        self.retrieval_strategy = opt['retrieval_strategy.name']

        if self.retrieval_strategy == 'triplet':
            self.criterion_retrieval = Triplet(
                opt,
                nb_classes,
                dim_emb,
                engine)
        elif self.retrieval_strategy == 'vlp_triplet':
            self.criterion_retrieval = VLPTriplet(
                opt,
                dim_emb,
                engine)
        elif self.retrieval_strategy == 'pairwise':
            self.criterion_retrieval = Pairwise(opt)

        elif self.retrieval_strategy == 'pairwise_pytorch':
            self.criterion_retrieval = nn.CosineEmbeddingLoss()
        else:
            raise ValueError('Unknown loss ({})'.format(self.retrieval_strategy))

        self.cross_encoder = opt.get('cross_encoder', False)
        
        if self.cross_encoder:
            self.cross_criterion = nn.CrossEntropyLoss()
            self.itm_loss_weight = opt.get('itm_loss_weight', 1)

    def forward(self, net_out, batch):
        if self.retrieval_strategy in ['triplet']:
            out = self.criterion_retrieval(net_out['image_embedding'],
                                           net_out['recipe_embedding'],
                                           batch['match'],
                                           batch['image']['class_id'],
                                           batch['recipe']['class_id'])
        elif self.retrieval_strategy in ['vlp_triplet']:
            out = self.criterion_retrieval(net_out['image_embedding'],
                                           net_out['recipe_embedding'],
                                           batch['match'],)

        elif self.retrieval_strategy == 'pairwise':
            out = self.criterion_retrieval(net_out['image_embedding'],
                                           net_out['recipe_embedding'],
                                           batch['match'])
        elif self.retrieval_strategy == 'pairwise_pytorch':
            out = {}
            out['loss'] = self.criterion_retrieval(net_out['image_embedding'],
                                                   net_out['recipe_embedding'],
                                                   batch['match'])

        if self.with_classif:
            out['image_classif'] = self.criterion_image_classif(net_out['image_classif'],
                                                                batch['image']['class_id'].squeeze(1))
            out['recipe_classif'] = self.criterion_recipe_classif(net_out['recipe_classif'],
                                                                  batch['recipe']['class_id'].squeeze(1))
            out['loss'] *= self.weight_retrieval
            out['loss'] += out['image_classif'] * self.weight_classif
            out['loss'] += out['recipe_classif'] * self.weight_classif

        if self.cross_encoder and self.itm_loss_weight > 0:
            out['loss']+= self.cross_criterion(net_out['cross_embedding'], net_out['cross_embedding_labels'])*self.itm_loss_weight
            
        return out
