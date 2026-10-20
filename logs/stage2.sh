cd /d/Research-Publishing/07-ncert-deletions/full-corpus
PY="../venv/Scripts/python -X utf8 -I"
$PY code/qa_pairs.py > logs/qa.out 2>&1
$PY code/compare_official2.py code/corpus_pairs.csv > logs/compare2.out 2>&1
$PY code/make_validation_sample.py code/pairs_english.csv 20261017 validation_fresh_WORKING.csv > logs/valsample.out 2>&1
$PY code/crosscheck.py code/corpus_pairs.csv 300 1 > logs/crosscheck.out 2>&1
$PY code/classify_rules.py code/corpus_pairs.csv --sample 60 --seed 3 > logs/classify.out 2>&1
echo STAGE2DONE >> logs/stage2.out
