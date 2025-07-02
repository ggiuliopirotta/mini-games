import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "chomp_component", path=os.path.dirname(__file__)
)


def render_chomp(n, m, available, game_on=True):
    """
    Render the Chomp grid using a custom Streamlit component.

    :param n: number of rows
    :param m: number of columns
    :param available: list of available cells to bite
    :param game_on: whether the game is active
    :return: dict
    """
    return _component_func(
        spec={"n": n, "m": m, "available": available, "game_on": game_on}, default=None
    )
