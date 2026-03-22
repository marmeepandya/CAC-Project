#!/bin/bash
#SBATCH --job-name=translation
#SBATCH --partition=gpu_a100_il
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --output=/home/ma/ma_ma/ma_mpandya/CAC/translation_%j.out
#SBATCH --error=/home/ma/ma_ma/ma_mpandya/CAC/translation_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=marmeep23@gmail.com

echo "Job started: $(date)"
module load cs/ollama/0.5.11
ollama serve &
OLLAMA_PID=$!
sleep 15
ollama pull llama3.1:8b
source /home/ma/ma_ma/ma_mpandya/CAC/.venv/bin/activate
cd /home/ma/ma_ma/ma_mpandya/CAC
python translate_run.py
kill $OLLAMA_PID
echo "Job finished: $(date)"
