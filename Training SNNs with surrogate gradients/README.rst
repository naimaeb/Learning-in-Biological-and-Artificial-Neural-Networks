**************************************************
Tutorial on Spiking Neural Networks
**************************************************

.. Comment: Only the README content after the inclusion marker below will be added to the documentation by sphinx.
.. content-inclusion-marker-do-not-remove

The goal of Tutorial 6 is to become familiar with spiking neural networks, and to use the surrogate method for training them. 
Specifically, you will be completing some key functions required for the implementation of a spiking neural network, trained to solve a classification task on the MNIST dataset. The functions to complete are in the modules :mod:`lib.spiking_functions` and :mod:`lib.spiking_layer`.
The tutorial is split in two weeks. The second week uses much of the same code as the first week, but has extra functions.

Tutorial 6.2 -- Dec. 2nd, 2020
###############################

In the second week of the tutorial, you are going to implement several key functions required for training a spiking network, namely you will implement 1) methods for using a surrogate gradient to train your spiking network, and 2) the functions to compute the loss and the accuracy on the spikes of the output units.

The code used in this tutorial is based on Friedemann Zenke's Spytorch tutorial:

    https://github.com/fzenke/spytorch/

Please refer to the :ref:`API <api-reference-label>` to get an overview of the coding structure.

You can test your implementations by following the instructions from the :ref:`testing <tests-reference-label>` page.

In addition, you can see your code in action via the script :mod:`main`. Please study the command-line arguments on how to use the script.
Note that since we are using a different loss compared to last week, you should use a different set of hyperparameters to make your network learn.
For this, please use the following command line arguments:

.. code-block:: console

  $ python3 main.py --spike_reg=1e-6 --weight_scale=0.3 --R=1e4 --tau_syn=5e-2 --tau_mem=12e-3 --size_hidden=500 --epochs=1

To get detailed information about each hyperparameter, type:

.. code-block:: console

  $ python3 main.py --help

**Please refer to the assignment sheet to obtain further information on how exercises have to be handed in and how they are graded.**
