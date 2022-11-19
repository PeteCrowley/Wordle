# shellcheck disable=SC2164
cd ~/Documents/Python/Wordle
source venv/bin/activate
python main.py $1
deactivate
cd