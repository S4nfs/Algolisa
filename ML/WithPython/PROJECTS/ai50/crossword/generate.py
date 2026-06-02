import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for crossword_slot_variable in self.domains.keys():
            
            # keep a list of bad words so we can delete them after the loop
            words_that_are_the_wrong_length = []
            
            # check all the possible words for this slot
            for potential_word_choice in self.domains[crossword_slot_variable]:
                if len(potential_word_choice) != crossword_slot_variable.length:
                    words_that_are_the_wrong_length.append(potential_word_choice)
                    
            for junk_word in words_that_are_the_wrong_length:
                self.domains[crossword_slot_variable].remove(junk_word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        did_we_actually_change_anything = False
        
        # figure out where these two slots cross each other
        where_they_intersect = self.crossword.overlaps[x, y]
        
        # if they don't even cross, we have nothing to worry about!
        if where_they_intersect is None:
            return False
            
        index_for_x_slot, index_for_y_slot = where_they_intersect
        
        words_we_need_to_throw_out_for_x = []
        
        # let's look at every word x could possibly be
        for word_option_for_x in self.domains[x]:
            found_a_match_for_y = False
            
            # and compare it to every word y could be
            for word_option_for_y in self.domains[y]:
                # if the letters match at the intersection, we're good!
                if word_option_for_x[index_for_x_slot] == word_option_for_y[index_for_y_slot]:
                    found_a_match_for_y = True
                    break
                    
            # if no word in y's domain works with this word in x, it's trash
            if not found_a_match_for_y:
                words_we_need_to_throw_out_for_x.append(word_option_for_x)
                did_we_actually_change_anything = True
                
        # toss out the bad words
        for bad_word in words_we_need_to_throw_out_for_x:
            self.domains[x].remove(bad_word)
            
        return did_we_actually_change_anything

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue_of_arcs_to_process = []
        
        # if they didn't give us arcs, we gotta start with every single overlapping pair
        if arcs is None:
            for first_slot in self.crossword.variables:
                for neighbor_slot in self.crossword.neighbors(first_slot):
                    queue_of_arcs_to_process.append((first_slot, neighbor_slot))
        else:
            # just use what they gave us
            queue_of_arcs_to_process = list(arcs)
            
        # LOL keep grinding until the queue is totally empty
        while len(queue_of_arcs_to_process) > 0:
            current_x_slot, current_y_slot = queue_of_arcs_to_process.pop(0)
            
            # did revising x against y actually change x's domain?
            if self.revise(current_x_slot, current_y_slot):
                
                # did we run out of words for x?
                if len(self.domains[current_x_slot]) == 0:
                    return False
                    
                # since x changed, we need to re-check all of x's neighbors (except y) to to make sure THEY are still consistent with x
                for other_neighbor_of_x in self.crossword.neighbors(current_x_slot):
                    if other_neighbor_of_x != current_y_slot:
                        queue_of_arcs_to_process.append((other_neighbor_of_x, current_x_slot))
                        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # check if every single variable on the board is in our assignment dictionary
        for crossword_slot in self.crossword.variables:
            if crossword_slot not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # hold all the words weve used so far to check for duplicates
        words_we_have_already_used = set()
        
        for slotted_variable, assigned_word in assignment.items():
            # Crossword RULE 1: every word must be unique
            if assigned_word in words_we_have_already_used:
                return False
            words_we_have_already_used.add(assigned_word)
            
            # Crossword RULE 2: word length has to exactly match the slot length
            if len(assigned_word) != slotted_variable.length:
                return False
                
            # Crossword RULE 3: no conflicting letters at intersections
            for neighbor_slot in self.crossword.neighbors(slotted_variable):
                # we only care if the neighbor actually has a word assigned to it right now
                if neighbor_slot in assignment:
                    neighbor_assigned_word = assignment[neighbor_slot]
                    my_overlap_index, their_overlap_index = self.crossword.overlaps[slotted_variable, neighbor_slot]
                    
                    # if the letters at the crossing dont match up this assignment is completely busted
                    if assigned_word[my_overlap_index] != neighbor_assigned_word[their_overlap_index]:
                        return False
                        
        # if we survived all those checks we are fine
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # map each word to how many neighbor options it ruins
        word_to_elimination_count_mapping = {}
        
        for potential_word_for_var in self.domains[var]:
            number_of_ruled_out_options = 0
            
            # check all neighbors that haven't been assigned yet
            for unassigned_neighbor in self.crossword.neighbors(var):
                if unassigned_neighbor not in assignment:
                    my_cross_idx, neighbor_cross_idx = self.crossword.overlaps[var, unassigned_neighbor]
                    
                    # how many words in the neighbor domain does this word break
                    for neighbor_word_option in self.domains[unassigned_neighbor]:
                        if potential_word_for_var[my_cross_idx] != neighbor_word_option[neighbor_cross_idx]:
                            number_of_ruled_out_options += 1
                            
            word_to_elimination_count_mapping[potential_word_for_var] = number_of_ruled_out_options
            
        # sort the words by the elimination count (lowest first)
        sorted_list_of_best_words = sorted(
            word_to_elimination_count_mapping.keys(),
            key=lambda specific_word: word_to_elimination_count_mapping[specific_word]
        )
        
        return sorted_list_of_best_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # collect everyone who isnt assigned yet
        slots_waiting_for_words = []
        for v in self.crossword.variables:
            if v not in assignment:
                slots_waiting_for_words.append(v)
                
        # sort them based on heuristic rules
        # primary key: fewest options left in domain (MRV)
        # secondary key (tiebreaker): most neighbors (highest degree) -> usse negative so it sorts descending
        slots_waiting_for_words.sort(
            key=lambda slot: (len(self.domains[slot]), -len(self.crossword.neighbors(slot)))
        )
        
        # just return the winner at the top of the pile
        return slots_waiting_for_words[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # base case: we filled the whole board
        if self.assignment_complete(assignment):
            return assignment
            
        # pick the smartest next slot to try filling
        slot_to_try_filling_now = self.select_unassigned_variable(assignment)
        
        # try the best words for this slot first
        for word_guess in self.order_domain_values(slot_to_try_filling_now, assignment):
            
            # make a tentative guess
            assignment[slot_to_try_filling_now] = word_guess
            
            # does this guess break the rules
            if self.consistent(assignment):
                
                # it looks okay so far let's keep going down this path
                result_from_going_deeper = self.backtrack(assignment)
                
                if result_from_going_deeper is not None:
                    # we found the solution pass it all the way back up
                    return result_from_going_deeper
                    
            # that didnt work out take the word back off the board
            del assignment[slot_to_try_filling_now]
            
        # tried every single word for this slot and nothing worked
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
