from importlib import resources
import tomllib

__version__ = "1.1.1"

guess_list = []

#Read default number of game guesses
_cfg = tomllib.loads(resources.read_text("rweintr_wordgame","config.toml"))
NUMBER_OF_GUESSES_EASY = _cfg["game"]["num_guesses_easy"]
NUMBER_OF_GUESSES_MEDIUM = _cfg["game"]["num_guesses_medium"]
NUMBER_OF_GUESSES_DIFFICULT = _cfg["game"]["num_guesses_difficult"]
WORD_LENGTH_EASY_MIN = _cfg["game"]["word_length_easy_min"]
WORD_LENGTH_EASY_MAX = _cfg["game"]["word_length_easy_max"]
WORD_LENGTH_MEDIUM_MIN = _cfg["game"]["word_length_medium_min"]
WORD_LENGTH_MEDIUM_MAX = _cfg["game"]["word_length_medium_max"]
WORD_LENGTH_DIFFICULT_MIN = _cfg["game"]["word_length_difficult_min"]
WORD_LENGTH_DIFFICULT_MAX = _cfg["game"]["word_length_difficult_max"]
EASY_LEVEL_MULTIPLIER = _cfg["scoring"]["easy_multiplier"]
MEDIUM_LEVEL_MULTIPLIER = _cfg["scoring"]["medium_multiplier"]
DIFFICULT_LEVEL_MULTIPLIER = _cfg["scoring"]["difficult_multiplier"]