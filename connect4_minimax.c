#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>


// -------------------------------------------------- //
// --- CONSTANTS AND TYPES -------------------------- //


#define ROWS 6
#define COLS 7
#define NONE 0
#define P1 1
#define P2 2


typedef struct {
    int board[ROWS][COLS];
    int heights[COLS];
} GameState;


// -------------------------------------------------- //
// --- GAME FUNCTIONS ------------------------------- //


bool is_valid_move(GameState *state, int col) {
    return state->heights[col] < ROWS;
}


void undo_move(GameState *state, int col) {
    if (state->heights[col] > 0) {
        state->heights[col]--;
        state->board[state->heights[col]][col] = NONE;
    }
}


void make_move(GameState *state, int col, int player) {
    if (is_valid_move(state, col)) {
        state->board[state->heights[col]][col] = player;
        state->heights[col]++;
    }
}


bool check_win(GameState *state, int player) {
    for (int r = 0; r < ROWS; r++) {
        for (int c = 0; c < COLS; c++) {
            if (state->board[r][c] == player) {
                // Horizontal
                if (c+3 < COLS &&
                    state->board[r][c+1] == player &&
                    state->board[r][c+2] == player &&
                    state->board[r][c+3] == player)
                    return true;
                // Vertical
                if (r+3 < ROWS &&
                    state->board[r+1][c] == player &&
                    state->board[r+2][c] == player &&
                    state->board[r+3][c] == player)
                    return true;
                // Diagonal (1st and 2nd)
                if (r-3 >= 0 && c+3 < COLS &&
                    state->board[r-1][c+1] == player &&
                    state->board[r-2][c+2] == player &&
                    state->board[r-3][c+3] == player)
                    return true;
                if (r+3 < ROWS && c+3 < COLS &&
                    state->board[r+1][c+1] == player &&
                    state->board[r+2][c+2] == player &&
                    state->board[r+3][c+3] == player)
                    return true;
            }
        }
    }
    return false;
}


bool check_immediate_win(GameState *state, int player) {
    bool win = false;

    for (int c = 0; c < COLS; c ++) {
        if (is_valid_move(state, c)) {
            make_move(state, c, player);
            win = check_win(state, player);
            undo_move(state, c);

            if (win) return true;
        }
    }
    return win;
}


bool is_full(GameState *state) {
    for (int c = 0; c < COLS; c++) {
        if (state->heights[c] < ROWS) {
            return false;
        }
    }
    return true;
}


bool is_terminal(GameState *state) {
    return is_full(state) || check_win(state, 1) || check_win(state, 2);
}


// -------------------------------------------------- //
// --- MOVE ORDERING -------------------------------- //


static const int static_ordering[COLS] = {3, 2, 4, 1, 5, 0, 6};


// -------------------------------------------------- //
// --- UTILS ---------------------------------------- //


void init_board(GameState *state) {
    for (int c = 0; c < COLS; c++) {
        for (int r = 0; r < ROWS; r++) {
            state->board[r][c] = NONE;
        }
        state->heights[c] = 0;
    }
}


void print_board(GameState *state) {
    for (int r = ROWS-1; r >= 0; r--) {
        for (int c = 0; c < COLS; c++) {
            printf("%d ", state->board[r][c]);
        }
        printf("\n");
    }
    printf("\n");
}


// -------------------------------------------------- //
// --- MINIMAX ALGORITHM ---------------------------- //


int negamax(
    GameState *state,
    int depth,
    int player,
    int alpha,
    int beta
) {
    
    // Return evaluation at a terminal state
    if (is_terminal(state)) {
        if (check_win(state, 3-player)) {
            return -(ROWS*COLS+1-depth);
        }
        return 0;
    }
    if (depth == 0) return 0;

    // Check if there is an immediate win
    if (check_immediate_win(state, player)) return (ROWS*COLS+1-depth);
    
    // Initialize the best eval
    int best_eval = INT_MIN;

    // Loop
    for (int i = 0; i < COLS; i++) {
        int c = static_ordering[i];
        if (is_valid_move(state, c)) {
            make_move(state, c, player);
            int eval = -negamax(state, depth-1, 3-player, -beta, -alpha);
            undo_move(state, c);
            
            best_eval = (eval > best_eval) ? eval : best_eval;
            alpha = (eval > alpha) ? eval : alpha;
            if (beta <= alpha) break;
        }
    }
    return best_eval;
}


int find_best_move(GameState *state, int player, int depth) {

    // Initialize the best move and eval
    int best_move = -1;
    int best_eval = INT_MIN;
    int alpha = -(ROWS*COLS/2);
    int beta = ROWS*COLS/2;

    if (player == P2) {
        alpha *= -1;
        beta *= -1;
    }

    // Loop
    for (int i = 0; i < COLS; i++) {
        int c = static_ordering[i];
        if (is_valid_move(state, c)) {
            make_move(state, c, player);
            int eval = -negamax(state, depth-1, 3-player, -beta, -alpha);
            undo_move(state, c);

            if (eval > best_eval) {
                best_eval = eval;
                best_move = c;
            }
            alpha = (eval > alpha) ? eval : alpha;
            if (beta <= alpha) break;

        }
    }
    return best_move;
}


// -------------------------------------------------- //
// --- MAIN FUNCTION -------------------------------- //


int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <depth>\n", argv[0]);
        return 1;
    }
    int depth = atoi(argv[1]);

    GameState state;
    init_board(&state);

    // Set the board state for debugging
    // int preset[ROWS][COLS] = {
    //     {1, 0, 1, 2, 2, 2, 1},
    //     {1, 0, 1, 2, 2, 2, 0},
    //     {1, 0, 0, 2, 2, 0, 0},
    //     {2, 0, 0, 1, 1, 0, 0},
    //     {1, 0, 0, 0, 0, 0, 0},
    //     {0, 0, 0, 0, 0, 0, 0},
    // };
    // for (int r = 0; r < ROWS; r++) {
    //     for (int c = 0; c < COLS; c++) {
    //         state.board[r][c] = preset[r][c];
    //     }
    // }
    // for (int c = 0; c < COLS; c++) {
    //     int h = 0;
    //     for (int r = 0; r < ROWS; r++) {
    //         if (state.board[r][c] != NONE) h++;
    //     }
    //     state.heights[c] = h;
    // }
    
    int me = P2;
    int p1_move;
    int p2_move;

    while (true) {
        
        p1_move = find_best_move(&state, P1, depth);
        make_move(&state, p1_move, P1);
        if (check_win(&state, P1)) {
            print_board(&state);
            printf("P1 wins!\n");
            break;
        }
        
        print_board(&state);
        printf("P2 -> Enter column (0-6): ");
        scanf("%d", &p2_move);
        if (!is_valid_move(&state, p2_move)) {
            printf("Invalid move.\n");
            continue;
        }
        make_move(&state, p2_move, P2);

        if (check_win(&state, P2)) {
            print_board(&state);
            printf("P2 wins!\n");
            break;
        }
    
        if (is_full(&state)) {
            print_board(&state);
            printf("It's a draw!\n");
            break;
        }
    }
}