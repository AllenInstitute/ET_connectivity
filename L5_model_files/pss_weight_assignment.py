#%% assign pss weights based on tuning angle
#%%
import numpy as np
import matplotlib.pyplot as plt
import sonata.circuit
import h5py 
import argparse
import shutil
import os
import json
import pandas as pd

#%%
def get_v1_dfs(basedir):
    data_files = [basedir + "/network/v1_nodes.h5"]
    data_type_files = [basedir + "/network/v1_node_types.csv"]
    v1 = sonata.circuit.File(data_files=data_files, data_type_files=data_type_files)
    v1df = v1.nodes["v1"].to_dataframe().copy()
    return v1df
    
def pick_core(df, radius=400.0):
    """return if the neuron is at the core."""
    lateral = np.sqrt(df["x"] ** 2 + df["z"] ** 2)
    return df[lateral <= radius]


def weight_assignment(v1df, target_angle=0, base_weight=10, sigma=60):
    tuning_angles = v1df["tuning_angle"].values
    x = tuning_angles - target_angle
    x[x>180] = x[x>180]-360
    x[x<-180] = x[x<-180]+360
    weights = base_weight*np.exp(-(x**2)/(2*sigma**2))
    v1df["Poisson_weight"] = weights
    return v1df

def pss_config(basedir,target_angle,sigma,top_dir):
    for recurrent in ['_recurrent','']:
        config = basedir+'/configs/config_'+top_dir+recurrent+'.json'
        with open(config, "r") as f:
            config_dict = json.load(f)
        config_dict["manifest"]["$BASE_DIR"] = \
            "${configdir}/../.."
        config_dict["manifest"]["$OUTPUT_DIR"] = \
            "$BASE_DIR/output_"+top_dir+"_all_angles_sigma"+str(sigma)\
            +"/output_"+top_dir+recurrent+"_angle"+str(target_angle)
        config_dict["networks"]["edges"][-1]["edges_file"] = \
            "$NETWORK_DIR/pss_v1_edges_all_angles_sigma"+str(sigma)\
            +"/pss_v1_edges_angle"+str(target_angle)+".h5"
        # save the modified config file as a new file
        new_config = basedir+"/configs/"+top_dir+"_all_angles_sigma"+str(sigma)\
        +"/config_"+top_dir+recurrent+"_angle"+str(target_angle)+".json"
        with open(new_config, "w") as f:
            json.dump(config_dict, f, indent=2)

def pss_config_single_neuron(basedir,id_select,w,top_dir):
    for recurrent in ['_recurrent','']:
        config = basedir+'/configs/config_'+top_dir+recurrent+'.json'
        with open(config, "r") as f:
            config_dict = json.load(f)
        config_dict["manifest"]["$BASE_DIR"] = \
            "${configdir}/../.."
        config_dict["manifest"]["$OUTPUT_DIR"] = \
            "$BASE_DIR/output_"+top_dir+"_single_neuron"\
            +"/output_"+top_dir+recurrent+"_neuron"+str(id_select)+"_w"+str(int(w))
        config_dict["networks"]["edges"][-1]["edges_file"] = \
            "$NETWORK_DIR/pss_v1_edges_single_neuron"\
            +"/pss_v1_edges_neuron"+str(id_select)+"_w"+str(int(w))+".h5"
        # save the modified config file as a new file
        new_config = basedir+"/configs/"+top_dir+"_single_neuron"\
        +"/config_"+top_dir+recurrent+"_neuron"+str(id_select)+"_w"+str(int(w))+".json"
        with open(new_config, "w") as f:
            json.dump(config_dict, f, indent=2)


#%%
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Modify the weight of the Poisson input."
    )
    parser.add_argument(
        "-o", 
        "--output_dir", 
        default = 'l5_circuit',
        help="The output directory."
    )
    parser.add_argument(
        "-bkg", 
        "--has_bkg", 
        default = 'yes',
        help="Whether the network has background input."
    )
    parser.add_argument(
        "-a", 
        "--all_angles", 
        action="store_true",
        default = False,
        help="Generate weights for all angle conditions."
    )
    parser.add_argument(
        "-n",
        "--single_neuron",
        action="store_true",
        default = False,
        help="stimulate a single neuron"
    )
    parser.add_argument(
        "-t", 
        "--target_angle", 
        default=0, 
        help="Specify a target angle in (0,360)."
    )
    # w = 5 for new model, w = 3 for old model
    parser.add_argument(
        "-w", 
        "--base_weight", 
        type=float, 
        default=5, 
        help="Specify the max weight."
    )
    parser.add_argument(
        "-s", 
        "--sigma", 
        type=int, 
        default=60, 
        help="Specify the sigma for the Gaussina distribution."
    )

    
    basedir = parser.parse_args().output_dir
    all_angles = parser.parse_args().all_angles
    single_neuron = parser.parse_args().single_neuron
    target_angle = parser.parse_args().target_angle
    base_weight = parser.parse_args().base_weight
    sigma = parser.parse_args().sigma
    has_bkg = parser.parse_args().has_bkg

    if has_bkg == 'yes':
        top_dir = 'pssbkg'
    elif has_bkg == 'no':
        top_dir = 'pss'
    elif has_bkg == 'weak':
        top_dir = 'pss_weakbkg'
        bkg_v1_edge = pd.read_csv(basedir+'/network/bkg_v1_edge_types.csv',sep=' ')
        bkg_v1_edge['syn_weight'] = bkg_v1_edge['syn_weight']*.5
        bkg_v1_edge.to_csv(basedir+'/network/bkg_v1_edge_types_weak.csv',sep=' ',index=False)
    else:
        raise ValueError("Invalid input for has_bkg.")
 

    v1df = get_v1_dfs(basedir)

    file = "/network/pss_v1_edges.h5"

    with h5py.File(basedir+file,'r+') as f_edges:
        target_node_id = f_edges["edges/pss_to_v1/target_node_id"][()]
        f_edges["edges/pss_to_v1/0/syn_weight"][()] = 0


    if all_angles:
        if not os.path.exists(basedir+"/network/pss_v1_edges_all_angles_sigma"+str(sigma)):
            os.mkdir(basedir+"/network/pss_v1_edges_all_angles_sigma"+str(sigma))
        if not os.path.exists(basedir+"/configs/"+top_dir+"_all_angles_sigma"+str(sigma)):
            os.mkdir(basedir+"/configs/"+top_dir+"_all_angles_sigma"+str(sigma))
        for target_angle in np.arange(0,360,15):
            print('target angle: ', target_angle)
            w_df = weight_assignment(v1df,target_angle, base_weight, sigma)
            new_file  = "/network/pss_v1_edges_all_angles_sigma"+str(sigma)\
                +"/pss_v1_edges_angle"+str(target_angle)+".h5"
            shutil.copyfile(basedir+file, basedir+new_file)
            with h5py.File(basedir+new_file,'r+') as f_edges:
                target_node_id = f_edges["edges/pss_to_v1/target_node_id"][()]
                f_edges["edges/pss_to_v1/0/syn_weight"][()] = w_df.loc[target_node_id]["Poisson_weight"].values
            print('create config file')
            pss_config(basedir,target_angle,sigma,top_dir)

    elif single_neuron:
        if not os.path.exists(basedir+"/network/pss_v1_edges_single_neuron"):
            os.mkdir(basedir+"/network/pss_v1_edges_single_neuron")
        if not os.path.exists(basedir+"/configs/"+top_dir+"_single_neuron"):
            os.mkdir(basedir+"/configs/"+top_dir+"_single_neuron")
        v1df = pick_core(v1df, radius=200)
        ETdf = v1df.query('pop_name == "e5ET"').reset_index(drop=True)
        node_ids = ETdf["node_id"].values
        # randomly pick 10 nodes with fixed random seed
        np.random.seed(0)
        ids_select = np.random.choice(node_ids,10,replace=False)
        for id in ids_select:
            print(id)
            new_file  = "/network/pss_v1_edges_single_neuron"\
            +"/pss_v1_edges_neuron"+str(id)+"_w"+str(int(base_weight))+".h5"
            shutil.copyfile(basedir+file, basedir+new_file)
            with h5py.File(basedir+new_file,'r+') as f_edges:
                target_node_id = f_edges["edges/pss_to_v1/target_node_id"][()]
                f_edges["edges/pss_to_v1/0/syn_weight"][target_node_id==id] = base_weight
            print('create config file')
            pss_config_single_neuron(basedir,id,base_weight,top_dir)    
    else:
        w_df = weight_assignment(v1df,target_angle, base_weight, sigma)
        with h5py.File(basedir+file,'r+') as f_edges:
            target_node_id = f_edges["edges/pss_to_v1/target_node_id"][()]
            f_edges["edges/pss_to_v1/0/syn_weight"][()] = w_df.loc[target_node_id]["Poisson_weight"].values


