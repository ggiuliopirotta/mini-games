#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>


// -------------------------------------------------- //
// --- CONSTANTS AND TYPES -------------------------- //


#define ROWS 6
#define HEIGHT (ROWS+1)
#define COLS 7


typedef struct {
    uint64_t position;  // Current player chips
    uint64_t mask;      // All chips
    int n_moves;
} Board;


// -------------------------------------------------- //
// --- BITBOARD ------------------------------------- //


/**
 * Generate a bitmask representing the bottom row of the board.
 * It looks like 00...0100000010...1...
 *                     >------<>---<
 *                         6+1   7
 *               >----<>--------------<
 *                 15         49
 * Where the only 1s are evenly spaced every 7 bits.
 */
static inline uint64_t bottom_mask() {
    uint64_t mask = 0;
    for (int col = 0; col < COLS; col ++) {
        // (1ULL << (col*HEIGHT)) shifts 1 by col*HEIGHT positions to get the 1st row of each column
        // Then just take the or to set the bit
        mask |= (1ULL << (col*HEIGHT));
    }
    return mask;
}

static inline uint64_t bottom_mask_col(int col) {
    // Just take the first row of the column
    return 1ULL << (col*HEIGHT);
}

/**
 * Generate a bitmask representing all valid positions of the board.
 * It looks like 00...0011111101..101..
 *                     >-----<>---<
 *                       6+1    7
 *               >----<>--------------<
 *                 15         49
 * Where the 1s are the first 6 rows for each column.
 */
static inline uint64_t board_mask() {
    // The binary multiplication by 0b(1ULL << HEIGHT)-1 = 63d turns any 1 into 111111
    return bottom_mask() * ((1ULL << HEIGHT)-1);
}

static inline uint64_t top_mask_col(int col) {
    // Just take the sixth row of the column
    return 1ULL << (col*HEIGHT + ROWS-1);

}
 
static inline uint64_t col_mask(int col) {
    // Just take the column bits
    return ((1ULL << ROWS)-1) << (col*HEIGHT);
}


// -------------------------------------------------- //
// --- BOARD OPERATIONS ----------------------------- //


void init_board(Board *board) {
    board->position = 0;
    board->mask = 0;
    board->n_moves = 0;
}

/**
 * Check whether the current player is in a winning position.
 * This is done in 3 phases:
 *      1. Shift the board by 1 position and check that there are 2 consecutive 1-bits
 *      2. Store the shifted bool board
 *      3. Shift the board again by two positions and check that there are 3 consecutive pairs of 1-bits
 *      => If so, there is a win
 * 
 * The process is repeated for each direction.
 */
bool check_win(uint64_t pos) {
    
    // Horizontal
    uint64_t pos_shift = pos & (pos >> HEIGHT);
    if(pos_shift & (pos_shift >> (2*HEIGHT))) return true;
    
    // 1st and 2nd diagonal
    pos_shift = pos & (pos >> ROWS);
    if(pos_shift & (pos_shift >> (2*ROWS))) return true;
    pos_shift = pos & (pos >> (HEIGHT+1));
    if(pos_shift & (pos_shift >> (2*(HEIGHT+1)))) return true;
    
    // Vertical
    pos_shift = pos & (pos >> 1);
    if(pos_shift & (pos_shift >> 2)) return true;
    
    return false;
}

bool is_valid_move(Board *board, int col) {
    // Check if the top row is free
    return (board->mask & top_mask_col(col)) == 0;
}

bool is_winning_move(Board *board, int col) {
    // Check if the move yields an immediate win to the current player
    uint64_t pos = board->position;
    pos |= (board->mask + bottom_mask_col(col)) & col_mask(col);
    return check_win(pos);
}

void make_move(Board *board, int col) {
    // Switch the player
    board->position ^= board->mask;
    // Set the bottom row of the column to 1
    board->mask |= board->mask + bottom_mask_col(col);
    board->n_moves ++;
}

bool is_full(Board *board) {
    return board->n_moves == ROWS*COLS;
}


// -------------------------------------------------- //
// --- POSITION EVALUATION -------------------------- //


int evaluate_position(Board *board) {
    return 0;
}


// -------------------------------------------------- //
// --- MOVE ORDERING -------------------------------- //


// First explore moves in the center
static const int static_ordering[COLS] = {3, 2, 4, 1, 5, 0, 6};


// -------------------------------------------------- //
// --- MINIMAX ALGORITHM ---------------------------- //


int negamax(Board *board, int depth, int alpha, int beta) {
    
    // Return the evaluation at terminal state
    if (depth == 0) return evaluate_position(board);
    if (is_full(board)) return 0;

    // Check if there is an immediate win
    for (int col = 0; col < COLS; col++) {
        if (is_valid_move(board, col) && is_winning_move(board, col)) {
            return ROWS*COLS+1-board->n_moves;
        }
    }

    // Initialize
    int best_eval = INT_MIN;
    
    // Loop over the columns
    for (int idx = 0; idx < COLS; idx++) {
        int col = static_ordering[idx];
        if (is_valid_move(board, col)) {
            Board child = *board;
            make_move(&child, col);
            int eval = -negamax(&child, depth-1, -beta, -alpha);
            best_eval = (eval > best_eval) ? eval : best_eval;
            alpha = (eval > alpha) ? eval : alpha;
            if (alpha >= beta) break;
        }
    }
    return best_eval;
}

int find_best_move(Board *board, int depth) {

    // Check if there is an immediate win
    for (int col = 0; col < COLS; col++) {
        if (is_valid_move(board, col) && is_winning_move(board, col)) {
            return col;
        }
    }

    // Initialize
    int best_move = -1;
    int best_eval = INT_MIN;
    int alpha = INT_MIN;
    int beta = INT_MAX;

    // Loop over the columns
    for (int idx = 0; idx < COLS; idx++) {
        int col = static_ordering[idx];
        if (is_valid_move(board, col)) {
            Board child = *board;
            make_move(&child, col);
            int eval = -negamax(&child, depth-1, -beta, -alpha);

            if (eval > best_eval) {
                best_eval = eval;
                best_move = col;
            }
            alpha = (eval > alpha) ? eval : alpha;
            if (alpha >= beta) break;
        }
    }
    return best_move;
}


// -------------------------------------------------- //
// --- PRINT ---------------------------------------- //


void print_board(Board *board) {
    for (int row = ROWS-1; row >= 0; row--) {
        for (int col = 0; col < COLS; col++) {
            uint64_t idx = 1ULL << (col*HEIGHT + row);
            if (board->mask & idx) {
                printf("%c ", (board->position & idx) ? 'x' : 'o');
            } else {
                printf(". ");
            }
        }
        printf("\n");
    }
    printf("\n");
}


// -------------------------------------------------- //
// --- MAIN FUNCTION -------------------------------- //


int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <depth>\n", argv[0]);
        return 1;
    }
    int depth = atoi(argv[1]);

    Board board;
    init_board(&board);
    int p1_move;
    int p2_move;

    while (true) {
        
        p1_move = find_best_move(&board, depth);
        make_move(&board, p1_move);
        if (check_win(board.position ^ board.mask)) {
            print_board(&board);
            printf("P1 wins!\n");
            break;
        }
        
        print_board(&board);
        printf("P2 -> Enter column (0-6): ");
        scanf("%d", &p2_move);
        if (!is_valid_move(&board, p2_move)) {
            printf("Invalid move.\n");
            continue;
        }
        make_move(&board, p2_move);

        if (check_win(board.position ^ board.mask)) {
            print_board(&board);
            printf("P2 wins!\n");
            break;
        }
    
        if (is_full(&board)) {
            print_board(&board);
            printf("It's a draw!\n");
            break;
        }
    }
    return 0;
}