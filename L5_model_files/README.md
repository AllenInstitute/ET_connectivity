# L5 circuit model with generalized leaky-integrate-and-fire (GLIF) neurons

## Overview

A project for making biorealistic model of mouse L5 circuit model of GLIF cells.

The L5 circuit model was built as a modified version of a bio-realistic model of the mouse primary visual cortex (<https://portal.brain-map.org/explore/models/mv1-all-layers>), from which we extracted the neuronal models for L5.

The L5 circuit model consists of 3 cell types: L5 ET cells, L5 Pvalb cells (Basket Cells), and L5 Sst cells (Martinotti Cells), which are represented by 40 unique generalized leaky-integrate-and-fire (GLIF) neuron models. Here we specifically adjusted the connection probabilities of L5 ET cells to these 3 cell types based on 12 proofread L5 ET cells. In the base model developed using these data, 8% of all connections from L5 ET cells target other L5 ET cells, 49% target L5 Pvalb cells (PeriTC, basket), and 43% target L5 Sst cells (distTC, Martinotti). 


## Requirements
To run the model, you will need to install:
- `BMTK`
- `nest-simulator`


## Folders and files

#### `base_props/`
Contains seed files necessary for building the network. Most files are in a human-readable format and can be edited.
- **`V1model_seed_file.xlsx`**: An Excel file defining general properties of each cell population. Edit this file to modify cell populations and their numbers.
- **`v1_conn_props_l5circuit.json`**: A JSON file containing general connection properties between cell populations.
- **`v1_conn_props_l5circuit_exc_prop_*.json`**: JSON files with modified excitatory-to-excitatory (E-to-E) and excitatory-to-inhibitory (E-to-I) connection probabilities.

#### `config_templates/`
Contains configuration templates for model simulations.

#### `glif_models/`
Includes neuron and synapse models.

#### `glif_props/v1_node_models.json`
Defines node information required to build the network.

#### `precomputed_props/bkg_v1_edge_types.csv`
A precomputed CSV file containing background (bkg) weights. Use this as the background edge file for the network.

## Scripts

#### `build_network.py`
Build the network. Example:
```bash
mkdir -p l5_circuit
mpirun -np 8 python build_network.py -f -o l5_circuit/network --fraction .6 --compression gzip v1 bkg pss
```

#### `bkg_spike_generation.py`
Generate background spike trains.

#### `pss_spike_generation.py`
Generate external spike trains for Gaussian inputs.

#### `pss_weight_assignment.py`
Assign weights of Gaussian inputs to the network.

#### `run_pointnet.py`
Run the simulation. Example: 
```bash
python run_pointnet.py l5_circuit/configs/pssbkg_all_angles_sigma60/config_pssbkg_recurrent_angle0.json
```