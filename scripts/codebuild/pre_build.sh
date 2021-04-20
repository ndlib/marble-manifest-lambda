echo "[Pre-Build phase - run unit tests] `date` in `pwd`"

python -m unittest discover ./test  ||  { echo 'Auto Tests Failed' ; exit 1; }
# python -m unittest discover ./manifest_lembda  ||  { echo 'Auto Tests Failed' ; exit 1; }
