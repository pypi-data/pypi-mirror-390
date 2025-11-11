# Scaffold-Constrained-Molecule-Generation
Scaffold-Constrained-Molecule-Generation
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# Data Preprocessing
## Input requirement:
#### Required columns: SMILES, MolIndex
#### Example:
python -i scripts/preprocessing/PreProcess_Distribute.py --filepath_sbatch=p44 --filepath_error=e44 --hpc_parition=rtx --filepath_input=/home/xiw14035/exp/SCMG/Datasets/ChEMBL_TautomerCleaned_TokenCleaned_Unique_WIdx.csv --filepath_config=/home/xiw14035/exp/SCMG/Datasets/conditions.json.example5 --epochs=50 --size_batch=2048 --smiles_random=Canonical --dataset_mult=1 --use_all_pairs=All --num_workers=16 --dirpath_sliced=PreProcess_DecoderOnly/Sliced --dirpath_scaffold_decorator=PreProcess_DecoderOnly/SD_Pairs_EncoderDecoder --dirpath_output=PreProcess_DecoderOnly/TrainingSets_EncoderDecoder --size_test=100000 --decoder_only=0 --run_preprocess_scaffold_decorator=1

####
<!-- [![Build Status](https://github.com/xinyuwang1209/SCMG.svg?branch=master)](https://github.com/xinyuwang1209/SCMG) -->



#### TF

debug4 small embedding

debug5 soft cross entroy loss (log_softmax and nll)

debug 6 soft cross entropy loss + kl div

debug 7 soft cross entropy loss + kl div + ull