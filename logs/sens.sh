cd /d/Research-Publishing/07-ncert-deletions/full-corpus
PY="../venv/Scripts/python -X utf8 -I"
$PY code/run_diff.py code/corpus_pairs.csv --k 4 --out results/sensitivity/k4 > logs/sens_k4.out 2>&1
$PY code/run_diff.py code/corpus_pairs.csv --k 8 --out results/sensitivity/k8 > logs/sens_k8.out 2>&1
$PY code/run_diff.py code/corpus_pairs.csv --no-fuzzy --out results/sensitivity/nofuzzy > logs/sens_nofuzzy.out 2>&1
echo SENSDONE > logs/sens.done
