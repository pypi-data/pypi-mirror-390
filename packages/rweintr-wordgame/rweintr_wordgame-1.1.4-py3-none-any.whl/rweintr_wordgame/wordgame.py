from wonderwords import RandomWord
from rweintr_wordgame import NUMBER_OF_GUESSES_EASY, NUMBER_OF_GUESSES_MEDIUM, NUMBER_OF_GUESSES_DIFFICULT, \
    WORD_LENGTH_EASY_MIN, WORD_LENGTH_EASY_MAX, WORD_LENGTH_MEDIUM_MIN, WORD_LENGTH_MEDIUM_MAX, \
    WORD_LENGTH_DIFFICULT_MIN, WORD_LENGTH_DIFFICULT_MAX

def choose_game_word(level):
    ''' choose a random word to guess '''
    r = RandomWord()
    if level == str(1): 
        return r.word(word_min_length=WORD_LENGTH_EASY_MIN,word_max_length=WORD_LENGTH_EASY_MAX)
    elif level == str(2):
        return r.word(word_min_length=WORD_LENGTH_MEDIUM_MIN,word_max_length=WORD_LENGTH_MEDIUM_MAX)
    elif level == str(3):
        return r.word(word_min_length=WORD_LENGTH_DIFFICULT_MIN,word_max_length=WORD_LENGTH_DIFFICULT_MAX)
    else:
        return r.word(word_min_length=WORD_LENGTH_MEDIUM_MIN,word_max_length=WORD_LENGTH_MEDIUM_MAX)

def init_guess_word(game_word):
    ''' initialize guess list with hyphens '''
    guess_word=[]
    for i in range(len(game_word)):
        guess_word.append("_")
    return guess_word

def set_game_level(level):
    ''' set number of guesses allowed based on difficulty level input by user '''
    if level == str(1):
        num_guesses = NUMBER_OF_GUESSES_EASY
    elif level == str(2):
        num_guesses = NUMBER_OF_GUESSES_MEDIUM
    elif level == str(3):
        num_guesses = NUMBER_OF_GUESSES_DIFFICULT
    else:
        num_guesses = NUMBER_OF_GUESSES_MEDIUM
    return num_guesses

def guess_the_word(game_word, guess_word, num_guesses):
    ''' prompt user to guess letter a configurable num of times '''
    guesses=0
    guess_list=[]
    while (guesses < num_guesses):
        letter_guess=input("Guess a letter: ")[:1]
        if letter_guess == "Q":
            return "Quit", guesses
        guess_list = add_to_guess_list(guess_list,letter_guess)
        guesses += 1
        # if user enters an asterisk, user can attempt to guess entire word
        if letter_guess == "*":
            if guess_whole_word(game_word):
                return True, guesses
            else:
                incorrect_guess(guess_word,game_word,num_guesses - guesses)
                continue
        if letter_guess in game_word:
            print("Good guess ",letter_guess," is in word")
        else:
            print("Too bad ",letter_guess," is NOT in word")
        display_guess(letter_guess,game_word,guess_word)
        print("\nLetters guessed: ",guess_list)
        # User has guessed all letters in word so can exit function
        if not "_" in guess_word:
            return True, guesses
        else:
            print("you have ",num_guesses-guesses," guess(es) remaining")
    return False, guesses

def display_guess(letter_guess,game_word,guess_word):
    ''' display guess word vertically with correct letter guesses '''
    for i in range(len(game_word)):
        if guess_word[i]=="_":
            if letter_guess==game_word[i]:
                guess_word[i]=letter_guess
                print(letter_guess)
            else:
                print(guess_word[i])
        else:
            print(guess_word[i])

def guess_whole_word(game_word):
    ''' Prompt user to guess game word and check if guess is correct '''
    word_guess = input("Enter your word guess: ")
    if word_guess == game_word:
        return True
    else:
        return False
    
def incorrect_guess(guess_word,game_word,guesses):
    ''' displays message for incorrect guesses and redisplays last guess '''
    print("Too bad, your guess is incorrect")
    print("you have ",guesses," guess(es) remaining")
    for i in range(len(game_word)):
        print(guess_word[i])
    return

def add_to_guess_list(guess_list,letter_guess):
    ''' adds guessed letter to list that can be displayed to user '''
    if letter_guess != "*" and letter_guess not in guess_list:
        guess_list.append(letter_guess)
    return guess_list