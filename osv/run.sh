cd osv-schema/tools/ghsa/
pipenv sync
pipenv shell
mkdir ../../../out
python3 dump_ghsa.py --token $GITHUB_TOKEN ../../../out
cd ../../../