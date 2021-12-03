from typing import Union, Optional
import torch
import torch.nn as nn
from .pack_dims import squeeze_class
from .stateful_layer import StatefulLayer


class ExpLeak(StatefulLayer):
    def __init__(self, 
                 tau_leak: Union[float, torch.Tensor],
                 shape: Optional[torch.Size] = None,
                 train_alphas: bool = False,
                 threshold_low: Optional[float] = None,
                 *args, 
                 **kwargs
                ):
        """
        Pytorch implementation of a exponential leaky layer, that is equivalent to an exponential synapse or a low-pass filter.

        Parameters
        ----------
        tau: float
            Rate of leak of the state
        """
        super().__init__(
            state_names = ['v_mem']
        )
        if train_alphas:
            self.alpha_leak = nn.Parameter(torch.exp(-1/tau_leak))
        else:
            self.tau_leak = nn.Parameter(tau_leak)
        self.threshold_low = threshold_low
        self.train_alphas = train_alphas
        if shape:
            self.init_state_with_shape(shape)

    @property
    def alpha_leak_calculated(self):
        return self.alpha_leak if self.train_alphas else torch.exp(-1/self.tau_leak)
    
    def forward(self, input_data: torch.Tensor):
        batch_size, time_steps, *trailing_dim = input_data.shape

        # Ensure the neuron state are initialized
        if not self.is_state_initialised() or not self.state_has_shape((batch_size, *trailing_dim)):
            self.init_state_with_shape((batch_size, *trailing_dim))

        alpha_leak = self.alpha_leak_calculated
        
        output_states = []
        for step in range(time_steps):
            # Decay membrane potential and add synaptic inputs
            self.v_mem = alpha_leak * self.v_mem + (1 - alpha_leak) * input_data[:, step]

            # Clip membrane potential that is too low
            if self.threshold_low:
                self.v_mem = torch.nn.functional.relu(self.v_mem - self.threshold_low) + self.threshold_low

            output_states.append(self.v_mem)

        return torch.stack(output_states, 1)
    
    @property
    def _param_dict(self) -> dict:
        """
        Dict of all parameters relevant for creating a new instance with same
        parameters as `self`
        """
        param_dict = super()._param_dict
        param_dict["tau_leak"] = self.tau_leak

        return param_dict


ExpLeakSqueeze = squeeze_class(ExpLeak)
