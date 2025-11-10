import rweintr_wordgame
from rweintr_wordgame import wordgame, game_scoring

def main():
    '''Guess a random word letter by letter'''

    name=input("Please enter your name\n")
    print("Welcome " + name + " to the RWEINTR Guess the Word game version " + rweintr_wordgame.__version__)

    level=input("Choose difficulty level 1(Easy) 2(Medium (default)) 3(Difficult): ")
    # difficulty level determines number of guesses user is allowed
    num_guesses = wordgame.set_game_level(level)
    print("You have ",num_guesses," guesses.")
    print("You can quit anytime by entering Q")

    #choose a random generated word
    game_word=wordgame.choose_game_word(level)
    #print (game_word)

    guess_word=wordgame.init_guess_word(game_word)

    #Guess the word in a configurable number of tries and test for success
    guess_successful, guesses = wordgame.guess_the_word(game_word,guess_word,num_guesses)
    if guess_successful == "Quit":
        return
    elif guess_successful:
        print(name," congrats you guessed the word ", game_word," in ",guesses, " guess(es)")
        score = game_scoring.calculate_score(guesses,level)
    else:
        print(name," better luck next time, the word was  ", game_word)
        score = 0
    #store score in db
    session = game_scoring.create_session()
    best_game = game_scoring.get_max_score(session,name)
    game_scoring.add_game(session,name,score)
    print(f"Player {name} score of {score} recorded")
    #check for high score
    if best_game.high_score is not None:
        if score > best_game.high_score:
            print(f"Congrats- this a new high score for you!")
    elif score > 0:
        print(f"Congrats- this a new high score for you!")
    #run historical stats?
    answer=input("Want to see your statistics (Y/N)?")
    if answer.upper()=="Y":
        game_scoring.show_stats(session,name)

if __name__ == "__main__":
    main()