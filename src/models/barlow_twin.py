from dataclasses import dataclass
from typing import List, Dict, Union, Any
import torch
from torch import nn
from transformers import (
    BartConfig,
    BartModel,
    PreTrainedModel,
)
from transformers.models.bart.modeling_bart import (
    shift_tokens_right,
    BartEncoder, BartDecoder, BartAttention,
)
from transformers.modeling_outputs import (
    BaseModelOutput,
)
from transformers.file_utils import ModelOutput
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def compute_loss_on_twins(z: List[torch.Tensor]) -> torch.Tensor:
    assert len(z) == 2, "for the moment, this works only on twin pairs, not for higher order"
    assert z[0].size() == z[1].size(), "z dims have to be equal for square cross correl matrix"
    # z = [t.cpu() for t in z]
    batch_size, z_dim = z[0].size()
    c = (z[0].T @ z[1]) / batch_size
    diag = c.diagonal()
    off_diag = c - torch.diag_embed(diag)
    loss_diag = (diag - 1) ** 2
    loss_off_diag = off_diag ** 2
    loss_diag = loss_diag.sum() / z_dim  # num elements of diag scales as n
    loss_off_diag = loss_off_diag.sum() / ((z_dim ** 2) - z_dim)  # num elements off_diag roughly scales as n^2 - n
    # if torch.cuda.is_available():
    #     loss_diag = loss_diag.cuda()
    #     loss_off_diag = loss_off_diag.cuda()
    #     c = c.cuda()
    return loss_diag, loss_off_diag, c


class LatentConfig(BartConfig):
    # inherited from BartConfig:
    #
    # vocab_size=50265,
    # max_position_embeddings=1024,
    # encoder_layers=12,
    # encoder_ffn_dim=4096,
    # encoder_attention_heads=16,
    # decoder_layers=12,
    # decoder_ffn_dim=4096,
    # decoder_attention_heads=16,
    # encoder_layerdrop=0.0,
    # decoder_layerdrop=0.0,
    # activation_function="gelu",
    # d_model=1024,
    # dropout=0.1,
    # attention_dropout=0.0,
    # activation_dropout=0.0,
    # init_std=0.02,
    # classifier_dropout=0.0,
    # scale_embedding=False,
    # use_cache=True,
    # num_labels=3,
    # pad_token_id=1,
    # bos_token_id=0,
    # eos_token_id=2,
    # is_encoder_decoder=True,
    # decoder_start_token_id=2,
    # forced_eos_token_id=2,

    keys_to_ignore_at_inference = ['supp_data']

    def __init__(
        self,
        freeze_pretrained: str = 'both',
        hidden_features: int = 100,
        z_dim: int = 128,
        sampling_iterations: int = 100,
        seq_length: int = 512,
        latent_var_loss: str = 'mmd',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.freeze_pretrained = freeze_pretrained
        self.hidden_features = hidden_features
        self.z_dim = z_dim
        self.sampling_iterations = sampling_iterations
        self.seq_length = seq_length
        self.latent_var_loss = latent_var_loss


class TwinConfig(LatentConfig):

    def __init__(self, lambd: float = None, mu: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.lambd = lambd  # not a typo; weight on off diagonal terms of twin loss
        self.mu = mu  # weight twin z loss vs the other losses


class TwinLMConfig(TwinConfig):

    def __init__(self, gamma: float = None, **kwargs):
        super().__init__(**kwargs)
        self.gamma = gamma


@dataclass
class LatentEncoderOutput(BaseModelOutput):
    # redefine them to preserve order
    last_hidden_state: torch.FloatTensor = None
    hidden_states = None
    attentions = None
    loss: torch.Tensor = None
    latent_variable: torch.Tensor = None
    representation: torch.Tensor = None
    hidden_before_latent: torch.Tensor = None
    supp_data: Dict[str, torch.Tensor] = None
    # inherited
    # last_hidden_state: torch.FloatTensor = None
    # hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    # attentions: Optional[Tuple[torch.FloatTensor]] = None


@dataclass
class TwinOutput(LatentEncoderOutput):
    loss: torch.Tensor = None
    last_hidden_state: List[torch.Tensor] = None
    representations: List[torch.Tensor] = None
    hidden_before_latent: List[torch.Tensor] = None
    latent_variable: List[torch.Tensor] = None
    supp_data: Dict[str, torch.Tensor] = None
    last_hidden_state: List[torch.FloatTensor] = None
    # hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    # attentions: Optional[Tuple[torch.FloatTensor]] = None


@dataclass
class TwinLMOutput(ModelOutput):
    loss: torch.Tensor = None
    logits: List[torch.Tensor] = None
    representations: List[torch.Tensor] = None
    hidden_before_latent: torch.Tensor = None
    supp_data: Dict[str, torch.Tensor] = None


class LatentEncoder(BartEncoder):

    def __init__(
        self,
        pretrained_encoder,
        config: LatentConfig
    ):
        super().__init__(config)
        self.config = config
        self.freeze_pretrained = self.config.freeze_pretrained
        self.model = pretrained_encoder
        # freeze the pretrained model
        if self.freeze_pretrained in ['both', 'encoder']:
            for param in self.model.parameters():
                param.requires_grad_(False)
        elif self.freeze_pretrained is None or self.freeze_pretrained in ['', 'decoder']:
            pass
        else:
            raise ValueError(f"not sure what to freeze or not with freeze_pretrained={self.freeze_pretrained}")

        self.d_encoder = self.model.config.d_model
        self.seq_length = self.config.seq_length
        self.pad_token_id = self.model.config.pad_token_id
        # latent vars
        self.hidden_features = self.config.hidden_features
        self.sampling_iterations = self.config.sampling_iterations
        self.z_dim = self.config.z_dim
        self.latent_var_loss = self.config.latent_var_loss
        # own layers
        self.act_fct = nn.GELU()
        self.vae_dropout = nn.Dropout(p=config.dropout)
        self.fc_compress = nn.Linear(self.d_encoder, self.hidden_features)
        self.norm_compress = nn.LayerNorm(self.hidden_features, elementwise_affine=False)
        if self.latent_var_loss == "mmd" or self.latent_var_loss is None:   # infoVAE
            self.fc_z_1 = nn.Linear(self.seq_length * self.hidden_features, self.z_dim)
        elif self.latent_var_loss == "kl" or "kl-mc":   # classical VAE
            self.fc_z_mean = nn.Linear(self.seq_length * self.hidden_features, self.z_dim)
            self.fc_z_logvar = nn.Linear(self.seq_length * self.hidden_features, self.z_dim)
        else:
            raise ValueError(f"unknown loss type on latent variable {self.latent_var_loss}")
        self.norm_z = nn.LayerNorm(self.z_dim, elementwise_affine=False)

    def forward(
        self,
        input_ids=None,
        **kwargs,
        # attention_mask=None,
        # head_mask=None,
        # inputs_embeds=None,
        # output_attentions=None,
        # output_hidden_states=None,
        # return_dict=None,
    ) -> LatentEncoderOutput:
        # encoder
        encoder_outputs: BaseModelOutput = self.model(input_ids=input_ids, **kwargs)
        x = encoder_outputs.last_hidden_state  # -> B x L x H_enc
        if self.freeze_pretrained in ['encoder', 'both']:
            x.requires_grad_(True)
        batch_size, length, hidden_size = x.size()  # batch_size B, length L, hidden_size H_enc
        assert length == self.seq_length, f"observed seq length {length} mismatches with config.seq_length {self.seq_length} with input_ids.size()={input_ids.size()}"
        # compress
        y = x  # keep x for later as residual
        y = self.vae_dropout(y)
        y = self.fc_compress(y)  # -> B x L x H (example: 32 example x 256 token x 256 hidden features)
        y = self.norm_compress(y)
        y = self.act_fct(y)
        hidden_before_latent = y  # for visualization
        y = y.view(batch_size, (self.seq_length * self.hidden_features))  # B x (L * H)  (example: 32 * 65_536)
        # latent var
        y = self.vae_dropout(y)
        # if self.latent_var_loss == "mmd":
        #     z = self.fc_z_1(y)  # -> B x Z  (example: 32 example x 128 dimensional latent var)
        #     z = self.norm_z(z)
        #     loss = compute_mmd_loss(z, self.sampling_iterations)
        #     representation = z
        # elif self.latent_var_loss == "kl":
        #     z_mean = self.fc_z_mean(y)  # -> B x Z
        #     z_logvar = self.fc_z_logvar(y)  # -> B x Z
        #     z_std = torch.exp(0.5 * z_logvar)
        #     # z = sample_z(self.z_dim, batch_size)
        #     # z = z + z_mean + z_std
        #     q = torch.distributions.Normal(z_mean, z_std)
        #     z = q.rsample()
        #     representation = self.norm_z(z_mean)  # for twin cross correlation: take latent before sampling
        #     loss = compute_kl_loss(z_mean, z_logvar)
        # elif self.latent_var_loss == "kl-mc":
        #     z_mean = self.fc_z_mean(y)  # -> B x Z
        #     z_logvar = self.fc_z_logvar(y)  # -> B x Z
        #     z_std = torch.exp(0.5 * z_logvar / 2)
        #     q = torch.distributions.Normal(z_mean, z_std)
        #     z = q.rsample()
        #     representation = self.norm_z(z_mean)  # for twin cross correlation: take latent before sampling
        #     loss = monte_carlo_kl_divergence(z, z_mean, z_std)
        # elif self.latent_var_loss is None:
        z = self.fc_z_1(y)  # -> B x Z  (example: 32 example x 128 dimensional latent var)
        z = self.norm_z(z)
        loss = torch.tensor(0)
        if torch.cuda.is_available():
            loss = loss.cuda()
        representation = z
        # else:
        #     raise ValueError(f"unknown loss type on latent variable {self.latent_var_loss}")

        supp_data = {
            "loss_z": loss,
        }

        return LatentEncoderOutput(
            last_hidden_state=encoder_outputs.last_hidden_state,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
            loss=loss,
            latent_variable=z,
            hidden_before_latent=hidden_before_latent,
            representation=representation,
            supp_data=supp_data,
        )


class LatentDecoder(BartDecoder):

    def __init__(
        self,
        pretrained_decoder,
        config: LatentConfig
    ):
        super().__init__(config)
        self.config = config
        self.freeze_pretrained = self.config.freeze_pretrained
        self.model = pretrained_decoder
        # freeze the pretrained model
        if self.freeze_pretrained in ['both', 'decoder']:
            for param in self.model.parameters():
                param.requires_grad_(False)
        elif self.freeze_pretrained is None or self.freeze_pretrained in ['', 'encoder']:
            pass
        else:
            raise ValueError(f"not sure what to freeze or not with freeze_pretrained={self.freeze_pretrained}")

        self.d_decoder = self.model.config.d_model
        self.seq_length = self.config.seq_length
        self.pad_token_id = self.model.config.pad_token_id
        self.decoder_start_token_id = self.model.config.decoder_start_token_id
        self.residuals = self.config.residuals
        # latent vars
        self.hidden_features = self.config.hidden_features
        self.z_dim = self.config.z_dim
        # own layers
        self.act_fct = nn.GELU()
        self.vae_dropout = nn.Dropout(p=config.dropout)
        self.fc_z_2 = nn.Linear(self.z_dim, self.seq_length * self.hidden_features)
        self.norm_decompress = nn.LayerNorm(self.seq_length * self.hidden_features, elementwise_affine=False)
        self.fc_decompress = nn.Linear(self.hidden_features, self.d_decoder)
        # self.post_init()

    def forward(
        self,
        input_ids=None,
        encoder_hidden_states=None,
        latent_variable=None,  # hallmark of VAE
        attention_mask=None,
        encoder_attention_mask=None,
        head_mask=None,
        cross_attn_head_mask=None,
        past_key_values=None,
        inputs_embeds=None,
        use_cache=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        z = latent_variable
        batch_size, z_dim = z.size()
        # decompress
        y = self.fc_z_2(z)  # -> B x (L * H)
        y = self.norm_decompress(y)
        y = self.act_fct(y)
        y = y.view(batch_size, self.seq_length, self.hidden_features)  # -> B x L x H
        y = self.fc_decompress(y)  # -> B x L x H_dec
        if self.residuals:
            y = encoder_hidden_states + y  # resnet style
        # decoder
        decoder_outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            encoder_hidden_states=y, # TRY FOR TESTING: encoder_hidden_states
            encoder_attention_mask=encoder_attention_mask,
            head_mask=head_mask,
            cross_attn_head_mask=cross_attn_head_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        return decoder_outputs
        # BaseModelOutputWithPastAndCrossAttentions
        # return LatentDecoderOutput(
        #     last_hidden_state=decoder_outputs.last_hidden_state,
        #     past_key_values=decoder_outputs.past_key_values,
        #     hidden_states=decoder_outputs.hidden_states,
        #     attentions=decoder_outputs.attentions,
        #     cross_attentions=decoder_outputs.cross_attentions,
        # )


class MyPreTrainedModel(PreTrainedModel):

    """A bit of an unfortunate consequence of encoding twin examples as list
    instead of using an additional dimension of a tensor is that the PreTrainedModel
    class needs to be modified in the obscure method estimate_tokens() called by the 
    equally obscure floating_point_ops(). Using PreTrainedModel as base class is useful
    to be able to load model with from_pretrained().
    """

    def estimate_tokens(self, input_dict: Dict[str, Union[torch.Tensor, Any]]) -> int:
        """
        Helper function to estimate the total number of tokens from the model inputs.

        Args:
            inputs (`dict`): The model inputs.

        Returns:
            `int`: The total number of tokens.
        """
        if self.main_input_name in input_dict:
            return input_dict[self.main_input_name][0].numel() + input_dict[self.main_input_name][1].numel()
        else:
            logger.warn(
                "Could not estimate the number of tokens of the input, floating-point operations will not be computed"
            )
            return 0

    def floating_point_ops(
        self, input_dict: Dict[str, Union[torch.Tensor, Any]], exclude_embeddings: bool = True
    ) -> int:
        # For models that inherit from [`PreTrainedModel`], uses that method to compute the number of
        #     floating point operations for every backward + forward pass. If using another model, either implement such a
        #     method in the model or subclass and override this method.

        """
        Get number of (optionally, non-embeddings) floating-point operations for the forward and backward passes of a
        batch with this transformer model. Default approximation neglects the quadratic dependency on the number of
        tokens (valid if `12 * d_model << sequence_length`) as laid out in [this paper](https://arxiv.org/pdf/2001.08361.pdf) section 2.1. Should be overridden for transformers with parameter
        re-use e.g. Albert or Universal Transformers, or if doing long-range modeling with very high sequence lengths.

        Args:
            batch_size (`int`):
                The batch size for the forward pass.

            sequence_length (`int`):
                The number of tokens in each line of the batch.

            exclude_embeddings (`bool`, *optional*, defaults to `True`):
                Whether or not to count embedding and softmax operations.

        Returns:
            `int`: The number of floating-point operations.
        """

        return 6 * self.estimate_tokens(input_dict) * self.num_parameters(exclude_embeddings=exclude_embeddings)


class Twin(MyPreTrainedModel):

    config_class = TwinConfig

    def __init__(
        self,
        config: TwinConfig,
        pretrained: BartModel
    ):
        super().__init__(config)
        pretrained_encoder = pretrained.get_encoder()
        # shared pretrained encoder
        self.encoders = nn.ModuleList([
            LatentEncoder(pretrained_encoder, config),
            LatentEncoder(pretrained_encoder, config),
        ])
        self.config = config
        self.mu = self.config.mu
        self.lambd = self.config.lambd

    def forward(
        self,
        input_ids: List[torch.Tensor] = None,
        attention_mask: List[torch.Tensor] = None,
        **kwargs
    ):
        outputs: List[LatentEncoderOutput] = [
            self.encoders[i](input_ids=input_ids[i], attention_mask=attention_mask[i], **kwargs)
            for i in range(len(input_ids))
        ]
        loss, loss_twin_z, loss_diag, loss_off_diag, cross_correl = self.all_losses(outputs)
        supp_data = {
                "loss_diag": loss_diag,
                "loss_off_diag": loss_off_diag,
                "loss_twin_z": loss_twin_z,
                "img_correl": cross_correl.unsqueeze(0),
            }
        supp_data = self.update_supp_data(supp_data, outputs)
        return TwinOutput(
            loss=loss,
            last_hidden_state=[out.last_hidden_state for out in outputs],
            representations=[out.representation for out in outputs],
            hidden_before_latent=[out.hidden_before_latent for out in outputs],
            latent_variable=[out.latent_variable for out in outputs],
            supp_data=supp_data
        )

    def all_losses(self, outputs):
        loss_diag, loss_off_diag, cross_correl = compute_loss_on_twins([out.representation for out in outputs])
        losses = torch.stack([out.loss for out in outputs])
        losses = losses.sum()
        loss_twin_z = self.mu * (loss_diag + self.lambd * loss_off_diag)
        loss = losses + loss_twin_z
        return loss, loss_twin_z, loss_diag, loss_off_diag, cross_correl

    @staticmethod
    def update_supp_data(supp_data, outputs):
        for i, out in enumerate(outputs):
            for k, v in out.supp_data.items():
                supp_data[f"{k}_{i}"] = v
        return supp_data


class TwinSEQ2SEQ(Twin):

    def __init__(
        self,
        config: TwinLMConfig,
        pretrained: BartModel
    ):
        super().__init__(config, pretrained)
        pretrained_decoder = pretrained.get_decoder()
        # two LatentDecoders with the shared pretrained_decoder; only the decompression is independent
        self.decoders = nn.ModuleList([
            LatentDecoder(pretrained_decoder, config),
            LatentDecoder(pretrained_decoder, config),
        ])
        self.lm_head = pretrained.lm_head
        self.embedding = pretrained.get_input_embeddings()
        self.gamma = config.gamma

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        head_mask=None,
        decoder_head_mask=None,
        cross_attn_head_mask=None,
        encoder_outputs=None,
        past_key_values=None,
        inputs_embeds=None,
        decoder_inputs_embeds=None,
        labels=None,
        use_cache=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):

        if labels is not None:
            if decoder_input_ids is None and decoder_inputs_embeds is None:
                decoder_input_ids = [
                    shift_tokens_right(
                        lbl, self.config.pad_token_id, self.config.decoder_start_token_id
                    )
                    for lbl in labels
                ]

        encoder_outputs: TwinOutput = super().forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict
        )
        decoder_outputs = [
           decoder(
                input_ids=decoder_input_ids[i],
                encoder_hidden_states=encoder_outputs.last_hidden_state[i],  # in BartModel encoder_hidden_states=encoder_outputs[0]
                latent_variable=encoder_outputs.latent_variable[i],
                # attention_mask=decoder_attention_mask[i],
                # encoder_attention_mask=attention_mask[i],
                # head_mask=decoder_head_mask[i],
                # cross_attn_head_mask=cross_attn_head_mask[i],
                # past_key_values=past_key_values[i],
                # inputs_embeds=decoder_inputs_embeds[i],
                # use_cache=use_cache,
                # output_attentions=output_attentions,
                # output_hidden_states=output_hidden_states,
                # return_dict=return_dict,
            ) for i, decoder in enumerate(self.decoders)
        ]

        # trainable language model head
        logits = [
            self.lm_head(out.last_hidden_state)
            for out in decoder_outputs
        ]
        supp_data = encoder_outputs.supp_data if encoder_outputs.supp_data is not None else {}

        # calculate composite loss
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_lm = self.gamma * sum([
                loss_fct(logits[i].view(-1, self.decoders[i].config.vocab_size), labels[i].view(-1))
                for i in range(len(input_ids))
            ])
            loss_z = encoder_outputs.loss  # loss on latent var
            loss = loss_lm + loss_z  # combine with language modelling loss
            supp_data['loss_lm'] = loss_lm  # keep track for plotting in TensorBoard
        else:
            loss = None
            supp_data['loss_lm'] = loss_lm = None

        return TwinLMOutput(
            loss=loss,
            logits=logits,
            representations=encoder_outputs.representations,
            supp_data=supp_data
        )
