import numpy as np
import h5py
import pathlib
import sys


def write_poisson_input(
    output_filename, n_neu=1, start_time=1.0, duration=3.0, binsize=2.5e-4, rate=1000, seed=0
):
    # time units are seconds, (inverse: Hz)

    nbins = int(duration / binsize)
    np.random.seed(seed)
    spike_bools = np.random.random([n_neu, nbins]) < (rate * binsize)
    spike_bools[:,0:int(start_time/binsize)-1]=False
    where = np.where(spike_bools)
    # spikes_time = (np.where(spike_bools)[0] + 1) * binsize  # to avoid 0, still second
    timestamps = (where[1] + 1) * binsize
    # nids = np.zeros_like(spikes_time, dtype=np.uint)
    nids = where[0]

    # save
    out_file = h5py.File(output_filename, "w")
    # out_file["spikes/gids"] = nids
    # add some random value to avoid the bad time stamps.
    # out_file["spikes/timestamps"] = timestamps * 1000 + 0.01  # in ms
    # let's use gzip level 6.
    out_file.create_dataset(
        "spikes/gids",
        data=nids,
        compression="gzip",
        compression_opts=6,
        shuffle=True,
    )
    out_file.create_dataset(
        "spikes/timestamps",
        data=timestamps * 1000 + 0.01,
        compression="gzip",
        compression_opts=6,
        shuffle=True,
    )
    out_file.close()
    return 0

if __name__ == "__main__":
    # try to write the bkg (let's make all of them)
    # basedir = "small"
    basedir = sys.argv[1]
    pathlib.Path(f"{basedir}/pss").mkdir(parents=True, exist_ok=True)
    n_neu=1
    pss_name = f"{basedir}/pss/pss_spikes_1kHz_10s.h5"
    write_poisson_input(pss_name, n_neu, duration=10.0,seed=1)