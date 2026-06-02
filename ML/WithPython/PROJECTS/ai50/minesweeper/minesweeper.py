import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells exactly equals the mine count, they must all be mines!
        if len(self.cells) == self.count:
            return self.cells.copy()
        
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If zero mines in this group, then every single cell is safee
        if self.count == 0:
            return self.cells.copy()
            
        # If the count isn't zero, dangerous
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If just confirmed this cell is a mine, we can cross it off our list
        # and reduce the remaining mine count for this sentence by 1.
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If we know this cell is completely safe, we just remove it from the sentence
        # without changing the mine count, because it wasn't a mine.
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the cell as visited
        self.moves_made.add(cell)

        # Mark it as completely safe
        self.mark_safe(cell)

        # Let's gather all the neighbors around this newly revealed cell
        surrounding_neighbor_cells = set()
        mines_already_found_nearby = 0

        # We need to look one cell up, down, left, and right, including diagonals
        for row_offset in range(cell[0] - 1, cell[0] + 2):
            for col_offset in range(cell[1] - 1, cell[1] + 2):
                
                # Skip the center cell (the one we just clicked)
                if (row_offset, col_offset) == cell:
                    continue
                    
                # Make sure the neighbor is actually on the board
                if 0 <= row_offset < self.height and 0 <= col_offset < self.width:
                    neighbor_coordinate = (row_offset, col_offset)
                    
                    # If we already know this neighbor is a mine, we subtract one from the count
                    if neighbor_coordinate in self.mines:
                        mines_already_found_nearby += 1
                        
                    # If it's not a known safe cell or mine, we add it to our unresolved group
                    elif neighbor_coordinate not in self.safes:
                        surrounding_neighbor_cells.add(neighbor_coordinate)

        # Let's create a new sentence based on what we just learned
        remaining_unresolved_mines = count - mines_already_found_nearby
        freshly_discovered_sentence = Sentence(surrounding_neighbor_cells, remaining_unresolved_mines)
        self.knowledge.append(freshly_discovered_sentence)

        # x Let's keep deducing new information until we can't find anything else!
        did_we_learn_something_new = True
        
        while did_we_learn_something_new:
            did_we_learn_something_new = False

            guaranteed_safe_cells = set()
            guaranteed_mine_cells = set()

            # First, check if any of our existing sentences have solved themselves
            for current_knowledge_sentence in self.knowledge:
                guaranteed_safe_cells.update(current_knowledge_sentence.known_safes())
                guaranteed_mine_cells.update(current_knowledge_sentence.known_mines())

            if guaranteed_safe_cells or guaranteed_mine_cells:
                did_we_learn_something_new = True
                
                # Mark everything we just figured out
                for safe_spot in guaranteed_safe_cells:
                    self.mark_safe(safe_spot)
                for dangerous_mine in guaranteed_mine_cells:
                    self.mark_mine(dangerous_mine)

            # Let's clean up any sentences that are completely empty now
            sentences_to_throw_away = [s for s in self.knowledge if len(s.cells) == 0]
            for obsolete_sentence in sentences_to_throw_away:
                self.knowledge.remove(obsolete_sentence)

            # Finally, let's see if we can combine sentences to learn even more (Subset method)
            brand_new_inferred_sentences = []
            
            for first_sentence in self.knowledge:
                for second_sentence in self.knowledge:
                    # Skip comparing a sentence to itself
                    if first_sentence == second_sentence:
                        continue
                        
                    # If sentence 1 is a strict subset of sentence 2, we can subtract them!
                    if first_sentence.cells.issubset(second_sentence.cells):
                        deduced_leftover_cells = second_sentence.cells - first_sentence.cells
                        deduced_leftover_count = second_sentence.count - first_sentence.count
                        
                        clever_new_sentence = Sentence(deduced_leftover_cells, deduced_leftover_count)
                        
                        # Only add it if we haven't seen it before
                        if clever_new_sentence not in self.knowledge and clever_new_sentence not in brand_new_inferred_sentences:
                            brand_new_inferred_sentences.append(clever_new_sentence)

            # If we inferred new sentences, add them and repeat the whole process!
            if brand_new_inferred_sentences:
                did_we_learn_something_new = True
                self.knowledge.extend(brand_new_inferred_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Let's look through all our known safe spots
        for potential_safe_spot in self.safes:
            # If we haven't already clicked it, let's go for it.
            if potential_safe_spot not in self.moves_made:
                return potential_safe_spot
                
        # If we couldn't find any new safe moves, return None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_possible_random_choices = []
        
        # Let's scan the whole board
        for row_index in range(self.height):
            for col_index in range(self.width):
                board_coordinate = (row_index, col_index)
                
                # Make sure we don't click somewhere we've been, or somewhere we KNOW is a mine
                if board_coordinate not in self.moves_made and board_coordinate not in self.mines:
                    all_possible_random_choices.append(board_coordinate)
                    
        # If we have options, let's just pick one randomly and hope for the best
        if all_possible_random_choices:
            return random.choice(all_possible_random_choices)
            
        # If the board is full  ..return None
        return None
