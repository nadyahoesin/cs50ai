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
    Xcounter = 0
    Ocounter = 0

    for row in board:
        for cell in row:
            if cell == X:
                Xcounter += 1
            elif cell == O:
                Ocounter += 1
    
    if Xcounter <= Ocounter:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_action = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                possible_action.append((i, j))

    return possible_action


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board_copy = copy.deepcopy(board)

    if board_copy[action[0]][action[1]] != EMPTY:
        raise Exception("Invalid action")
    else:
        board_copy[action[0]][action[1]] = player(board)

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(len(board)):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY:
            return board[i][0]
        elif board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    elif board[2][0] == board[1][1] == board[0][2] and board[0][2] != EMPTY:
        return board[2][0]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

# Based on pseudocode in Lecture 0
def maxValue(board):
    value = -1000

    if terminal(board):
        return utility(board), None

    for action in actions(board):
        currentValue, prevAction = minValue(result(board, action))
        # Immediately return value if optimal value (1 for maxValue) 
        # is the current value, as that value will be maintained 
        if currentValue == 1:
            return currentValue, action
        else:
            value = max(value, currentValue)

    for action in actions(board):
        currentValue, prevAction = minValue(result(board, action))
        if currentValue == value:
            return currentValue, action


# Based on pseudocode in Lecture 0
def minValue(board):
    value = 1000

    if terminal(board):
        return utility(board), None

    for action in actions(board):
        currentValue, prevAction = maxValue(result(board, action))
        # Immediately return value if optimal value (-1 for minValue) 
        # is the current value, as that value will be maintained
        if currentValue == -1:
            return currentValue, action
        else:
            value = min(value, currentValue)
    
    for action in actions(board):
        currentValue, prevAction = maxValue(result(board, action))
        if currentValue == value:
            return currentValue, action


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        value, action = maxValue(board)
        return action
    else:
        value, action = minValue(board)
        return action
