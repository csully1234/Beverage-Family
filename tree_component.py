"""A two-way Streamlit custom component for the full-family SVG explorer.

Unlike an ordinary st.iframe, declare_component can return the selected
relative's ID to Python so the People selector and focused tree stay in sync.
"""
from pathlib import Path

import streamlit.components.v1 as components

TREE_COMPONENT = components.declare_component(
    "beverage_full_family_explorer",
    path=str(Path(__file__).resolve().parent / "static" / "tree_component"),
)


def show_full_tree(html: str, selected_id: str = "", height: int = 850):
    return TREE_COMPONENT(
        html=html,
        selected_id=str(selected_id or ""),
        height=height,
        key="beverage_family_tree_bridge",
        default=None,
    )
