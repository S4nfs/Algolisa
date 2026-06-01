"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Let's count how many Xs and Os are on the board to figure out whose turn it is.
    total_x_pieces_on_the_board = 0
    total_o_pieces_on_the_board = 0
    
    for current_row_index in range(3):
        for current_column_index in range(3):
            if board[current_row_index][current_column_index] == X:
                total_x_pieces_on_the_board += 1
            elif board[current_row_index][current_column_index] == O:
                total_o_pieces_on_the_board += 1
                
    # Since X always goes first, if they have the same amount of pieces, it must be X's turn!
    if total_x_pieces_on_the_board > total_o_pieces_on_the_board:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Gather all the empty spots into a set
    available_moves_for_current_player = set()
    
    for row_coordinate_index in range(3):
        for col_coordinate_index in range(3):
            # If the spot is empty, the player can totally move here
            if board[row_coordinate_index][col_coordinate_index] == EMPTY:
                available_moves_for_current_player.add((row_coordinate_index, col_coordinate_index))
                
    return available_moves_for_current_player


def result(board, action):
    """
    Return s the board that results from making move (i, j) on the board.
    """
    # First, make sure we aren't modifying the original board by creating a deep copy
    deep_copied_board_state = copy.deepcopy(board)
    
    the_row_for_the_move, the_column_for_the_move = action
    
    # We gotta check if this move is actually allowed
    if deep_copied_board_state[the_row_for_the_move][the_column_for_the_move] is not EMPTY:
        raise Exception("Hey! This spot is already taken, you can't move here!")
        
    # Find out whose turn it is and place their piece
    current_player_making_the_move = player(board)
    deep_copied_board_state[the_row_for_the_move][the_column_for_the_move] = current_player_making_the_move
    
    return deep_copied_board_state


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Let's check all the rows first to see if anyone got three across
    for row_index_to_check in range(3):
        if board[row_index_to_check][0] == board[row_index_to_check][1] == board[row_index_to_check][2] and board[row_index_to_check][0] is not EMPTY:
            return board[row_index_to_check][0]
            
    # Now let's check all the columns for three down
    for col_index_to_check in range(3):
        if board[0][col_index_to_check] == board[1][col_index_to_check] == board[2][col_index_to_check] and board[0][col_index_to_check] is not EMPTY:
            return board[0][col_index_to_check]
            
    # Time to check the two diagonals!
    # Top-left to bottom-right
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
        
    # Top-right to bottom-left
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
        
    # Looks like nobody has won yet (or it's a tie)
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # The game is definitely over if someone has won
    if winner(board) is not None:
        return True
        
    for checking_row_index in range(3):
        for checking_col_index in range(3):
            if board[checking_row_index][checking_col_index] == EMPTY:
                return False
                
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Let's see who the actual winner is
    the_winner_of_the_game = winner(board)
    
    if the_winner_of_the_game == X:
        return 1
    elif the_winner_of_the_game == O:
        return -1
    else:
        # TIE
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # If the game is already finished, there's no move to make
    if terminal(board):
        return None
        
    the_player_whose_turn_it_is = player(board)
    
    if the_player_whose_turn_it_is == X:
        # X is trying to maximize the score, so we'll start with something super low <<<
        best_possible_score_for_x = -float("inf")
        best_possible_move_for_x = None
        
        # Lets explore every single move X could potentially make :)
        for potential_action_to_try in actions(board):
            score_for_this_specific_action = finding_the_minimum_value(result(board, potential_action_to_try))
            if score_for_this_specific_action > best_possible_score_for_x:
                best_possible_score_for_x = score_for_this_specific_action
                best_possible_move_for_x = potential_action_to_try
                
        return best_possible_move_for_x
        
    else:
        # O is trying to minimize the score, so we'll start with something super high
        best_possible_score_for_o = float("inf")
        best_possible_move_for_o = None
        
        # Lets explored every single move O could potentially make
        for potential_action_to_try in actions(board):
            score_for_this_specific_action = finding_the_maximum_value(result(board, potential_action_to_try))
            if score_for_this_specific_action < best_possible_score_for_o:
                best_possible_score_for_o = score_for_this_specific_action
                best_possible_move_for_o = potential_action_to_try
                
        return best_possible_move_for_o



def finding_the_maximum_value(the_current_board_state):
    # This is for when it's X's turn, they want the highest number possible
    if terminal(the_current_board_state):
        return utility(the_current_board_state)
        
    highest_score_found_so_far = -float("inf")
    for action_to_explore in actions(the_current_board_state):
        highest_score_found_so_far = max(highest_score_found_so_far, finding_the_minimum_value(result(the_current_board_state, action_to_explore)))
        
    return highest_score_found_so_far
    
def finding_the_minimum_value(the_current_board_state):
    # This is for when it's O's turn, they want the lowest number possible
    if terminal(the_current_board_state):
        return utility(the_current_board_state)
        
    lowest_score_found_so_far = float("inf")
    for action_to_explore in actions(the_current_board_state):
        lowest_score_found_so_far = min(lowest_score_found_so_far, finding_the_maximum_value(result(the_current_board_state, action_to_explore)))
        
    return lowest_score_found_so_far
