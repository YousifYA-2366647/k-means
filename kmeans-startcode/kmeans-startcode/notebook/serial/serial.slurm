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
hostname
g++ --version 2>&1 | head -1

REF=/data/leuven/303/vsc30380/kmeans_serial_reference
IN=../datasets/100000x5.csv
SEED=2364763
K=10
REP=20
OUT=results_serial.csv

echo "label,type,blocks,threads,file,seed,clusters,repetitions,bestdist,time" > $OUT

for i in $(seq 1 10); do
  echo "RUN $i"
  echo -n "mine," >> $OUT
  ./kmeans --input $IN --output t_mine.csv --k $K --repetitions $REP --seed $SEED >> $OUT
  echo -n "ref," >> $OUT
  $REF     --input $IN --output t_ref.csv  --k $K --repetitions $REP --seed $SEED >> $OUT
done
cmp t_mine.csv t_ref.csv && echo "juiste output"
