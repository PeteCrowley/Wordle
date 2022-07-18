# shellcheck disable=SC2164
cd Documents/Python/Wordle
source venv/bin/activate.fish
python main.py $argv
deactivate
cd