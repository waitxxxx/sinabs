# Release notes

## 0.3
This is a major overhaul which restructures a large part of the package. 

* Addition of leaky models such as Leaky Integrate and Fire (LIF), Exponential Leaky (ExpLeak) and Adaptive LIF (ALIF).
* Activation module: under sinabs.activation you'll now be able to pick and choose different spike generation, reset mechanism and surrogate gradient functions. You can pass them to the neuron model (LIF, IAF, ...) of your liking if you want to change the default behavior.
* Support for EXODUS and Sinabs-Dynapcnn