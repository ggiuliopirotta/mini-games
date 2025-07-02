import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "connect4_component", path=os.path.dirname(__file__)
)


def render_connect4(grid, valid_columns=None, game_on=True):
    """
    Render the Connect 4 grid using a custom Streamlit component.

    :param grid: 2D list representing the game state
                 (0 = empty, 1 = player 1/red, 2 = player 2/yellow)
    :param valid_columns: list of column indices where moves are valid
    :param game_on: whether the game is active
    :return: dict with 'column' of clicked column, or None
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 7

    # If no valid columns specified, find columns that aren't full
    if valid_columns is None:
        valid_columns = []
        for col in range(cols):
            if grid[0][col] == 0:  # Top row is empty
                valid_columns.append(col)

    return _component_func(
        spec={
            "rows": rows,
            "cols": cols,
            "grid": grid,
            "valid_columns": valid_columns,
            "game_on": game_on,
        },
        default=None,
    )
