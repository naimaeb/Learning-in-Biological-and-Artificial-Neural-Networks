#!/usr/bin/env python3
# Copyright 2020 Maria Cervera, Matilde Farinha
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Implementing, training, and evaluating a spiking neural network (:mod:`lib.spiking_functions`)
--------------------------------------------------------------------------------------------------

The module :mod:`lib.spiking_functions` contains custom functions that should
be used for running, training and evaluating spiking networks. Specifically,
you must implement the surrogate gradient for the spiking nonlinearity, as well 
as the functions computing the loss and the accuracy on the spike trains of the 
output neurons. You will also implement a function that calculates a 
regularization loss term on the spiking activities.

New functionality can be added to
autograd_ by creating a subclass of class :class:`torch.autograd.Function`.
If you have pasted your answer to :meth:`lib.spiking_functions.spike_function`
from last week, then the forward pass
:meth:`torch.autograd.Function.forward` is already implemented for you in
:meth:`lib.spiking_functions.SurrogateSpike.forward`.

As discussed in the lecture and in the exercise session, we will use the
derivative of the hard-sigmoid function for the surrogate gradient. The
code for the backward pass :meth:`torch.autograd.Function.backward`,
with normalisation and scaling, is already
implemented for you in :meth:`lib.spiking_functions.SurrogateSpike.forward`.
What is missing is the function that calculates the surrogate
gradient: :meth:`lib.spiking_functions.derivative_hard_sigmoid`. You must derive
and implement the gradient of the hard-sigmoid function.

You will also implement the loss function
:meth:`lib.spiking_functions.loss_on_spikes`, the accuracy function
:meth:`lib.spiking_functions.accuracy_on_spikes` and the function that
computes the regularization loss term
:meth:`lib.spiking_functions.spike_regularizer`.


.. autosummary::
    lib.spiking_functions.derivative_hard_sigmoid
    lib.spiking_functions.spike_function
    lib.spiking_functions.SurrogateSpike
    lib.spiking_functions.SurrogateSpike.forward
    lib.spiking_functions.SurrogateSpike.backward
    lib.spiking_functions.loss_on_spikes
    lib.spiking_functions.accuracy_on_spikes
    lib.spiking_functions.spike_regularizer


.. _autograd:
    https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html

.. math:
    \usepackage{dsfont}

"""

# Please fill out identification details in
#   lib/spiking_layer.py
#   lib/spiking_functions.py
#   theory_question.txt

# Student name : Naima Elosegui Borras
# Student ID   : ID: 20-742-755	
# Email address: nelosegui@student.ethz.ch


import torch
import torch.nn as nn
from torch.autograd import Function

cross_entropy_loss = nn.CrossEntropyLoss()

def derivative_hard_sigmoid(x):
    r"""The analytic derivative of the hard-sigmoid function.

    This function implements the derivative of 
    the hard-sigmoid function with respect to the input :math:`x`,
    :math:`deriv (\cdot)`, defined as

    .. math::
        deriv(x) :=
        \begin{cases}
            0, & x < 0 \vee x \geq 1\\
            1, & 0 \leq x < 1\\
        \end{cases}
        :label: eq-hard_sigmoid_deriv

    Args: 
        x (torch.tensor): Input on which to compute the derivative.
    
    Returns:
       (torch.tensor): The derivative of the hard-sigmoid on x.
    
    """

    
    values_1 = torch.tensor([1.0])

    S_0 = torch.heaviside(x, values_1) 
    S_1 = torch.heaviside(x-1, values_1) 
    
    
    
    return S_0-S_1



def spike_function(D):
    r"""Spike non-linearity function.

    This function takes :math:`D = ( U - U_{threshold} )` as input,
    which is the amount by which the membrane potential of neurons is above the
    membrane threshold :math:`U_{threshold} \in \mathbb{R}`. There are :math:`M`
    neurons in a layer and minibatch size is :math:`B`, hence
    :math:`D \in \mathbb{R}^{B \times M}`.

    This function computes the spiking nonlinearity, which should
    produce a spike when a neuron's membrane potential exceeds or is equal
    to the membrane threshold potential i.e. when :math:`U_i - U_{threshold}
    \geq 0`.

    The spiking nonlinearity we use here is the simple Heaviside step function,
    :math:`\Theta (\cdot)`, defined as

    .. math::
        \Theta(x) :=
        \begin{cases}
            0, & x < 0 \\
            1, & x \geq 0
        \end{cases}
        :label: eq-heaviside

    Last week, you coded the :meth:`spike_function` method to
    take :math:`D = ( U - U_{threshold} ) \in \mathbb{R}^{B \times M}` as 
    input and compute :math:`\Theta(D)` elementwise for each entry in the 
    matrix. This is the same function. You should paste the code you wrote last
    week for that function in this week's function.

    Args:
        D: A matrix of shape :math:`B \times M` representing
            :math:`U - U_{threshold}`, the difference between the membrane
            potential of each of the :math:`M` neurons in each of the
            :math:`B` images of the mini-batch.

    Returns:
        The output spikes, obtained by applying :math:`\Theta (\cdot)`
        (defined in eq. :eq:`eq-heaviside`) elementwise to D.

    """
    values = torch.tensor([1.0])

    S = torch.heaviside(D, values)
    
    return S


def loss_on_spikes(S, T):
    r"""Computes cross entropy loss based on the spike trains of the output 
    units.

    Takes a set of output spikes in form of a tensor
    :math:`S \in \mathbb{R}^{B \times t_{max} \times M}`,
    where :math:`B` denotes the size of the mini-batch, :math:`t_{max}` the 
    number of timesteps during which each mini-batch is presented, and :math:`M` 
    the number of output units. Additionally, it takes a set of target labels
    :math:`T \in \mathbb{N}^{B}`, indicating the true class of each image
    :math:`b` in the current mini-batch.

    The loss calculated here is the cross-entropy loss applied to the
    average number of spikes over all timesteps for each output neuron for each
    image.

    It is calculated as follows:

    Let :math:`Z_{b,i} = \sum_t S_{b,t,i}/t_{max}` be the total number of spikes over
    all timesteps for each output neuron :math:`i` for each image :math:`b`, divided by the total number of timesteps.
    Then calculate the cross entropy loss:

    .. math::
        CELoss(Z, T) = \frac{1}{B} \sum_{b=1}^{B} - Z_{b, T_b} +
        \log \left( \sum_j \exp ( Z_{b, j} ) \right)

    You may wish to refer to the pytorch documentation for its native
    :class:`torch.nn.CrossEntropyLoss` class and use it.

    Args:
        S: The output spike trains, i.e., the matrix :math:`S`.
        T: The target activations, i.e., the matrix :math:`T`.

    Returns:
        (float): The cross entropy loss on the average of number of spikes.
    """
    
    Z = torch.mean(S, dim = 1)
    cross_ent_loss = cross_entropy_loss(Z,T)
    return cross_ent_loss


def accuracy_on_spikes(S, T):
    r"""Computes classification accuracy of the spiking network based on the
    spike trains of the output units.

    Takes a set of output spikes in form of a matrix
    :math:`S \in \mathbb{R}^{B \times t_{max} \times M}`,
    where :math:`B` denotes the size of
    the mini-batch, :math:`t_{max}` the number of timesteps during which each
    mini-batch is presented, and :math:`M` the number of output units. 
    Additionally, this ``Function`` requires a set of targets
    :math:`T \in \mathbb{Z}^{B}`, indicating the correct classes of the current
    mini-batch.

    Using these two arguments, it finds the output neurons that have the highest
    membrane spiking rate for each image, and compares these with the target 
    labels to compute the accuracy.

    Letting :math:`Z_{b,i} = \sum_t S_{b,t,i}/t_{max}` be the total number of spikes over
    all timesteps for each output neuron :math:`i` for each image :math:`b`, divided by the total number of timesteps,

    .. math::
        Accuracy = \frac{1}{B} \sum_{b=1}^{B} 1[ \arg\max_{i} Z_{b,:} = T_b]

    where :math:`1[\cdot]` is the indicator function.

    Args:
        S: The output spike trains, i.e., the matrix :math:`S`.
        T: The target classes, i.e., the vector :math:`T`.

    Returns:
        (float): The classification accuracy of the current batch.

    """
    batch_size = T.shape[0]
    
    Z = torch.mean(S, dim = 1)
    Y = torch.argmax(Z, dim = 1)
    
    Target_diff = Y-T
    
    count = 0   
    for diff in Target_diff:
        if diff == 0:
            count = count +1
    acc = torch.tensor([count/batch_size])
 
    return acc


def spike_regularizer(spikes_list):
    r"""Calculate the regularization loss term for the spiking activity.

    Biological neurons usually do not fire at rates greater than around 20Hz.
    In order to regularise our networks so that the neurons do not fire at
    grossly unphysiological rates, we calculate an additional term to add to
    the training loss.

    Many different types of regularization could work. Here you should implement
    a regularization term that has two components:

    The first component sums all the spikes over all hidden layers, batch
    elements, timesteps and neurons, i.e.

    .. math::
        \sum_{l} \sum_{i=1}^{M_l} \sum_{b, t} S_{l,b,t,i}

    where :math:`M_l` is the number of neurons in the hidden layer :math:`l`. 
    This corresponds to an L1 regularization on the total number of spikes at 
    the population, thus inducing sparsity at a population level.

    The second component regularizes the firing of individual neurons.
    It takes the mean squared sum of spikes for individual neurons (summed
    across batch elements and timestes), summed over all hidden layers, i.e.

    .. math::
        \sum_l \frac{1}{M_l} \sum_{i=1}^{M_l} \Big(\sum_{b,t} S_{l,b,t,i}\Big)^2

    This corresponds to an L2 norm in the firing rate of individual neurons,
    thus inducing neurons to have low firing rates.

    Finally, the regularization loss term returned by this function consists of 
    the sum of these two components.

    Please note that the inputs to this function only correspond to hidden 
    spiking activity. Therefore you do not have to exclude any
    layers within this function because it is already done for you.

    Args:
        spikes_list (list): a list of tensors of spikes, where each element
            corresponds to the spiking activity of a hidden layer and has shape 
            :math:`B` (batch size) :math:`\times t_{max}` (number of timesteps 
            :math:`\times M_l` (number of hidden units in that layer).

    Returns:
        (float): The regularization loss term.

    """
    L1 = 0.0
    L2 = 0.0
    
    for layer in spikes_list:
        num_units = layer.shape[2]
        sum_t_b = torch.sum(layer, (0, 1))
        L1 = L1 + torch.sum(sum_t_b)
        L2 = L2 + (1/num_units)*torch.sum(torch.square(sum_t_b))
    reg_loss = L1 +L2
    return reg_loss


class SurrogateSpike(Function):
    r"""A class to house the functions for the forward and backward passes of a 
    spiking nonlinearity.

    Because this class is an instance of :class:`torch.autograd.Function`,
    we are able to use all of PyTorch's autograd functionality. It has two
    components: the forward function and the backward function.

    If you have pasted your answer to
    :meth:`lib.spiking_functions.spike_function`
    from last week, then the forward pass
    :meth:`torch.autograd.Function.forward` is already implemented for you.

    For the backward pass, typically we take the partial derivative of the
    forward nonlinearity with respect to each element of the inputs that
    is tagged as requiring the gradient. However, the gradient
    of the step function (and many other spiking non-linearities)
    is zero everywhere except at 0 where it is ill-defined. Therefore it is
    necessary to use the gradient of a different function for the backward
    pass. This is the 'surrogate gradient'.

    Here we will take the derivative of the hard-sigmoid function with respect to 
    its input as the surrogate gradient, as implemented in 
    :meth:`lib.spiking_functions.derivative_hard_sigmoid`.

    """

    @staticmethod
    def forward(ctx, D):
        r"""Computes the output of a spiking layer.

        In the forward pass we compute a step function of the input Tensor
        and return it. This directly applies your :meth:`spike_function()`
        implemented already for last week's tutorial.

        Args:
            ctx: A context. Should be used to store activations that are needed
                in the backward pass. To achieve this we use the
                ctx.save_for_backward method.
            D: A matrix of shape :math:`B \times M` representing
                :math:`U_{b,i} - U_{threshold}`, the difference between the 
                membrane potential of each of the :math:`M` neurons in each of 
                the :math:`B` mini-batches.

        Returns:
            The output spikes, obtained by applying :math:`\Theta` (defined in
            eq. :eq:`eq-heaviside`) elementwise to D.

        """
        ctx.save_for_backward(D)

        return spike_function(D)

    @staticmethod
    def backward(ctx, grad_output):
        r"""Computes the surrogate gradient of the spiking layer.

        In the backward pass we receive a Tensor D we need to compute the
        surrogate gradient of the loss with respect to the input, which
        represents the difference between the membrane potential of the layer
        and the membrane threshold:
        :math:`D = ( U_{i} - U_{threshold} ) \in \mathbb{R}^{B \times M}`.
        Here we use the partial derivative of the hard-sigmoid function
        with respect to all input tensors that are flagged to require
        gradients.

        Args:
            ctx: A context.
        Returns:
            grad (torch.tensor): The gradient of the loss with respect to the
                input.

        """
        D, = ctx.saved_tensors
        grad_input = grad_output.clone()
        grad = grad_input * derivative_hard_sigmoid(D)
        
        return grad