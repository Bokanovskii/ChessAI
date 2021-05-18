import chess 
import time
import random

pawnstable = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0]

knightstable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]
bishopstable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]
rookstable = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0]
queenstable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]
kingstable = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]

def evaluate(board): 
    # count of each piece left
    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    # material socre: location independent weighted summation of material pieces left on board
    material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)
    # sum of piece-square values weighted by piece position
    def PieceSquare(pieceType, table):
        piecesqW = sum([table[i] for i in board.pieces(pieceType, chess.WHITE)])
        piecesqB = sum([-table[chess.square_mirror(i)] for i in board.pieces(pieceType, chess.BLACK)])
        return piecesqW + piecesqB
    pawnsq = PieceSquare(chess.PAWN, pawnstable)
    knightsq = PieceSquare(chess.KNIGHT, knightstable)
    bishopsq = PieceSquare(chess.BISHOP, bishopstable)
    rooksq = PieceSquare(chess.ROOK, rookstable)
    queensq = PieceSquare(chess.QUEEN, queenstable)
    kingsq = PieceSquare(chess.KING, kingstable)

    # evaluation func -- white is positive
    eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
    #print(eval)
    if board.turn:
        return eval 
    else:
        return -eval

def quiescence(depth, maximizingPlayer, alpha, beta, board, iterations):
    # evaluate 'quiet' positions: all captures
    iterations += 1
    if board.is_checkmate():
        if maximizingPlayer: # white turn
            return -9999, None, iterations
        else:
            return 9999, None, iterations
    if board.is_stalemate():
        return 0, None, iterations
    if board.is_insufficient_material():
        return 0, None, iterations
    evalToRet = 0
    # order captures by MVV/LVA: for each capture compute the value of (victim - attacker) then search largest captures first
    def givesCheckmate(board, move):
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return True
        board.pop()
        return False
    captureMoves = list(filter(lambda move: board.is_capture(move) or givesCheckmate(board, move), board.legal_moves))

    # finish the quiecence search
    if depth == 0 or captureMoves is None or len(captureMoves) == 0:
        return evaluate(board), None, iterations

    for move in captureMoves:
        board.push(move)
        if maximizingPlayer:
            eval, blah, iterations = quiescence(depth - 1, False, alpha, beta, board, iterations)
            board.pop()
            evalToRet = max(eval, -9999)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        else:
            eval, blah, iterations = quiescence(depth - 1, True, alpha, beta, board, iterations)
            board.pop()
            evalToRet = min(eval, 9999)
            beta = min(beta, eval)
        if (beta <= alpha):
            break
    return evalToRet, None, iterations

# alpha: minimum score for the maximizing player
# beta: maximum score for the minimizng player
# when beta < alpha stop recurse
# maximize pruning by move ordering of likely better moves first (i.e. pawn takes queen)
def minimax(depth, maximizingPlayer, alpha, beta, board, iterations):
    iterations += 1
    maxEval = -9999
    minEval = 9999
    moveToMake = None
    # main minimax
    if depth == 0 or board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material():
        #return quiescence(maximizingPlayer, alpha, beta);
        return quiescence(7, maximizingPlayer, alpha, beta, board, iterations)
    legal_moves = list(board.legal_moves)
    if maximizingPlayer:   
        for move in legal_moves:
            board.push(move)
            eval, posMove, iterations = minimax(depth - 1, False, alpha, beta, board, iterations)
            board.pop()

            if eval > maxEval:
                moveToMake = move
                maxEval = eval

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval, moveToMake, iterations
    else:
        for move in legal_moves:
            board.push(move)
            eval, posMove, iterations = minimax(depth - 1, True, alpha, beta, board, iterations)
            board.pop()

            if eval < minEval:
                moveToMake = move
                minEval = eval

            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval, moveToMake, iterations
        
def main():
    board = chess.Board()
    
    while not board.is_game_over():
        print(board)
        if board.turn:
            algoRet = minimax(3, True, -9999, 9999, board, 0)
        else:
            algoRet = minimax(3, False, -9999, 9999, board, 0)
        move = algoRet[1]
        print()
        print("Leaves: " + str(algoRet[2]))
        # if move is None:
        #     board.push(list(board.legal_moves)[0])
        #     print(board)
        board.push(move)

    if board.turn:
        print("White wins!")
    else:
        print("Black wins!")

if __name__ == "__main__":
    main()
