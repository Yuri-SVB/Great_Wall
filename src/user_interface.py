import sys

class UserInterface:
    def __init__(self):
        self.index_input_str = ""
        self.index_input_int = 0
        self.index_input_is_valid = False
        self.user_chosen_input = ""

    def get_TLP_param(self) :
        print("Choose TLP parameter --- # of iterations of memory-hard hash")
        self.index_input_is_valid = False
        while not self.index_input_is_valid:
            self.index_input_str = sys.stdin.readline().strip()
            try:
                self.index_input_int = int(self.index_input_str)
                if self.index_input_int <= 0:
                    print('parameter has to be a positive integer')
                    # self.index_input_is_valid = False # it was already False
                else:
                    self.index_input_is_valid = True
            except ValueError:
                # Handle the exception
                print('Please enter an integer')

    def get_Li_branch_choice(self, tree_arity, level, shuffled_sentences) :
        choose_message = "\nChoose 1, ..., %d for level %d"
        choose_message += "" if level < 1 else ", choose 0 to go back"
        print(choose_message % (tree_arity, level))
        [print(sentence) for sentence in shuffled_sentences]

        self.index_input_is_valid = False
        while not self.index_input_is_valid:
            self.index_input_str = sys.stdin.readline().strip()
            try:
                self.index_input_int = int(self.index_input_str)
                if self.index_input_int == 0:
                    if level < 1:
                        print('You cannot go back at this point. This is level 0.')
                        # self.index_input_is_valid = False # it was already False
                    else:
                        self.index_input_is_valid = True
                else:
                    if 1 <= self.index_input_int and self.index_input_int <= tree_arity:
                        self.index_input_is_valid = True
                    else:
                        print('Index must be within valid range.')
                        # self.index_input_is_valid = False # it was already False
            except ValueError:
                # Handle the exception
                print('Please enter an integer')