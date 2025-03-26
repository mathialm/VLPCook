import os
import sys

import lmdb
import torch
import pickle
import h5py
from PIL import Image
import argparse
from tqdm import tqdm


def encode(value):
    return pickle.dumps(value)

def decode(bytes_value):
    return pickle.loads(bytes_value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_data', type=str,
                        help='path to root')
    args = parser.parse_args()
    dir_data = args.dir_data
    path_hdf5 = os.path.join(dir_data, 'data.h5')
    dir_lmdb = os.path.join(dir_data, 'data_lmdb')
    os.system('mkdir -p ' + dir_lmdb)
    hdf5_file = h5py.File(path_hdf5, 'r')

    for split in ['val', 'test', 'train']:
        print('Converting ' + split + 'set')
        dir_split = os.path.join(dir_lmdb, split)
        os.system('mkdir -p ' + dir_split)

        convert_ims(dir_split, hdf5_file, split)

        convert_ids(dir_split, hdf5_file, split)

        convert_numims(dir_split, hdf5_file, split)

        convert_impos(dir_split, hdf5_file, split)

        convert_classes(dir_split, hdf5_file, split)

        convert_imnames(dir_split, hdf5_file, split)


def convert_imnames(dir_split, hdf5_file, split):
    print('Converting imnames')
    path_lmdb = os.path.join(dir_split, 'imnames.lmdb')
    env = lmdb.open(path_lmdb, map_size=1e12)
    with env.begin(write=True, buffers=True) as txn:
        for i in tqdm(range(len(hdf5_file['/imnames_' + split]))):
            value = hdf5_file['/imnames_' + split][i]
            value = value.decode()
            value = os.path.basename(value)
            txn.put(encode(i), encode(value))


def convert_classes(dir_split, hdf5_file, split):
    print('Converting classes')
    path_lmdb = os.path.join(dir_split, 'classes.lmdb')
    env = lmdb.open(path_lmdb, map_size=1e12)
    with env.begin(write=True, buffers=True) as txn:
        for i in tqdm(range(len(hdf5_file['/classes_' + split]))):
            value = hdf5_file['/classes_' + split][i]
            value = int(value)
            txn.put(encode(i), encode(value))


def convert_impos(dir_split, hdf5_file, split):
    print('Converting impos')
    path_lmdb = os.path.join(dir_split, 'impos.lmdb')
    env = lmdb.open(path_lmdb, map_size=1e12)
    with env.begin(write=True, buffers=True) as txn:
        for i in tqdm(range(len(hdf5_file['/impos_' + split]))):
            value = hdf5_file['/impos_' + split][i]
            value = value.tolist()
            txn.put(encode(i), encode(value))


def convert_numims(dir_split, hdf5_file, split):
    print('Converting numims')
    path_lmdb = os.path.join(dir_split, 'numims.lmdb')
    env = lmdb.open(path_lmdb, map_size=1e12)
    with env.begin(write=True, buffers=True) as txn:
        for i in tqdm(range(len(hdf5_file['/numims_' + split]))):
            value = hdf5_file['/numims_' + split][i]
            value = int(value)
            txn.put(encode(i), encode(value))


def convert_ids(dir_split, hdf5_file, split):
    print('Converting ids')
    path_lmdb = os.path.join(dir_split, 'ids.lmdb')
    env = lmdb.open(path_lmdb, writemap=True, map_size=1e12)
    with env.begin(write=True, buffers=True) as txn:
        for i in tqdm(range(len(hdf5_file['/ids_' + split]))):
            value = hdf5_file['/ids_' + split][i]
            value = value.decode()  #  already in binary
            txn.put(encode(i), encode(value))


def convert_ims(dir_split, hdf5_file, split):
    print('Converting ims')
    path_lmdb = os.path.join(dir_split, 'ims.lmdb')
    env = lmdb.open(path_lmdb, writemap=True, map_size=1e12)
    try:
        with env.begin(write=True, buffers=True) as txn:
            for i in tqdm(range(len(hdf5_file['/imnames_' + split]))):  # image left are 0 (=useless)
                i_enc = encode(i)

                if txn.get(i_enc) is not None:
                    continue

                value = hdf5_file['/ims_' + split][i]
                value = Image.fromarray(value.transpose((1, 2, 0)))
                txn.put(i_enc, encode(value))

    except Exception as e:
        print(e.with_traceback())


if __name__ == '__main__':
    print("Converting h5 file to lmdb")
    main()




