import torch
from typing import List
from torch import nn
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .barlow_twin import Twin, TwinSEQ2SEQ, LatentEncoder
from ..config import config

PRETRAINED_BARLOW = config.embedding_model['barlow']


class LatentEmbedding:

    def __init__(self, pretrained_barlow: str = PRETRAINED_BARLOW, mode: str = 'paragraph'):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained('facebook/bart-base')
        pretrained_bart = AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-base')
        if "no-lm" in pretrained_barlow:  # no language model
            full_twin_model = Twin.from_pretrained(pretrained_barlow, pretrained=pretrained_bart)
        else:  # with language model
            full_twin_model = TwinSEQ2SEQ.from_pretrained(pretrained_barlow, pretrained=pretrained_bart)
        encoder_idx = 0 if mode == 'sentence' else 1
        self.encoder: LatentEncoder = full_twin_model.encoders[encoder_idx]
        self.encoder.eval()
        # freeze the parameters
        for p in self.encoder.parameters():
            p.requires_grad = False
        self.seq_len = full_twin_model.config.seq_length

    def __call__(self, inputs: List[str]) -> torch.Tensor:
        # test if string and make a list if so
        tokenized = self.tokenizer(
            inputs,
            return_tensors="pt",
            padding="max_length",
            max_length=self.seq_len,
            truncation=True
        )
        input_ids = tokenized['input_ids']
        outputs = self.encoder(input_ids)
        representation = outputs.representation
        representation = torch.nn.functional.normalize(representation)
        return representation


class LatentSentenceEmbedding(LatentEmbedding):
    def __init__(self, pretrained: str = PRETRAINED_BARLOW):
        super().__init__(pretrained, mode='sentence')


class LatentParagraphEmbedding(LatentEmbedding):
    def __init__(self, pretrained: str =PRETRAINED_BARLOW):
        super().__init__(pretrained, mode='paragraph')
