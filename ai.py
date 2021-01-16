from chess import BLACK, WHITE

PAWN_EVAL_WHITE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]

PAWN_EVAL_BLACK = list(reversed(PAWN_EVAL_WHITE))

KNIGHT_EVAL = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
    [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
    [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
    [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
    [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
    [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]

BISHOP_EVAL_WHITE = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
    [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
    [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
    [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
    [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]

BISHOP_EVAL_BLACK = list(reversed(BISHOP_EVAL_WHITE))

ROOK_EVAL_WHITE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
]

ROOK_EVAL_BLACK = list(reversed(ROOK_EVAL_WHITE))

QUEEN_EVAL = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]

KING_EVAL_WHITE = [
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
]

KING_EVAL_BLACK = list(reversed(KING_EVAL_WHITE))

PIECE_EVALS = {
    'P': {
        WHITE: PAWN_EVAL_WHITE,
        BLACK: PAWN_EVAL_BLACK
    },
    'K': {
        WHITE: KING_EVAL_WHITE,
        BLACK: KING_EVAL_BLACK
    },
    'Q': {
        WHITE: QUEEN_EVAL,
        BLACK: QUEEN_EVAL
    },
    'R': {
        WHITE: ROOK_EVAL_WHITE,
        BLACK: ROOK_EVAL_BLACK
    },
    'N': {
        WHITE: KNIGHT_EVAL,
        BLACK: KNIGHT_EVAL
    },
    'B': {
        WHITE: BISHOP_EVAL_WHITE,
        BLACK: BISHOP_EVAL_BLACK
    }
}

PIECE_COSTS = {
    'P': 10,
    'K': 900,
    'Q': 90,
    'R': 50,
    'N': 30,
    'B': 30,
}


def get_piece_eval(piece, pos):
    if piece is None:
        return 0

    row, col = pos
    char = piece.raw_char()
    color = piece.get_color()

    ev = PIECE_EVALS[char]
    table = ev[color]

    return table[row][col]


def get_piece_cost(piece):
    if piece is None:
        return 0

    char = piece.raw_char()
    return PIECE_COSTS[char]


def get_absolute_value(piece, pos):
    if piece is None:
        return 0

    return get_piece_cost(piece) + get_piece_eval(piece, pos)


def get_piece_value(piece, pos):
    if piece is None:
        return 0

    value = get_absolute_value(piece, pos)
    color = piece.get_color()

    if color == BLACK:
        value = -1 * value

    return value


def evaluate_board(board):
    totalEvaluation = 0

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            totalEvaluation = totalEvaluation + get_piece_value(cell, (i, j))

    return totalEvaluation


def minimax(depth, game, alpha, beta, is_maximising_player):
    if depth == 0:
        return -1 * evaluate_board(game.get_board())

    new_game_moves = game.moves_without_check()

    if is_maximising_player:
        bestMove = -9999

        for i, move in enumerate(new_game_moves):
            game.make_move(*move, True)

            minim = minimax(depth - 1, game, alpha, beta, not is_maximising_player)

            bestMove = max(bestMove, minim)

            game.undo(True)

            alpha = max(alpha, bestMove)
            if beta <= alpha:
                return bestMove

        return bestMove
    else:
        bestMove = 9999

        for i, move in enumerate(new_game_moves):
            game.make_move(*move, True)

            minim = minimax(depth - 1, game, alpha, beta, not is_maximising_player)

            bestMove = min(bestMove, minim)

            game.undo(True)

            beta = min(beta, bestMove)
            if beta <= alpha:
                return bestMove

        return bestMove


def minimax_root(depth, game, is_maximising_player):
    new_game_moves = game.moves_without_check()
    best_move_found = new_game_moves[0]
    best_move = -9999

    for i, move in enumerate(new_game_moves):
        game.make_move(*move, True)

        value = minimax(depth - 1, game, -10000, 10000, not is_maximising_player)

        game.undo()

        if value >= best_move:
            best_move = value
            best_move_found = move

    return best_move_found
