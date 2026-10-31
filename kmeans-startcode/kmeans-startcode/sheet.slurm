#!/bin/bash -l
#SBATCH --cluster=mindwell
#SBATCH --account=llp_h_pds
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:30:00
#SBATCH --error="%x.e%A"
#SBATCH --output="%x.o%A"

source /data/leuven/303/vsc30380/slurmhooks
module purge
module load GCC/14.3.0
module load Python
hostname
g++ --version 2>&1 | head -1

REF=/data/leuven/303/vsc30380/kmeans_serial_reference
IN=../datasets/100000x5.csv

python compare.py ./kmeans $REF --input $IN --output cmp_form.csv \
  --k 10 --repetitions 20 --seed 1337

# 10 metingen
for i in $(seq 1 10); do
  ./kmeans --input $IN --output someoutput.csv --k 10 --repetitions 20 --seed 1337
done

