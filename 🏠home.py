from src.chomp.chomp_st import init_chomp_state
from src.c4.c4_st import init_connect4_state
from src.kuhn.kuhn_st import init_kuhn_state
import streamlit as st


### -------------------------------------------------- ###
### --- PAGE MARKDOWN -------------------------------- ###


st.set_page_config(page_title="Giulio's web app")


init_chomp_state()
init_connect4_state()
init_kuhn_state()


# Welcome message
st.markdown(
    """
    # Welcome to My Web App 👋
    ---
    ### About

    I like solving games and that's why I created this web app.  
    Here you can play some, but I bet you can't beat my superhuman algorithms 😏

    As of now, the games are:  
    - **Kuhn Poker**
    - **Connect 4 in a row**
    - **Chomp**
    
    All of them can be accessed from the sidebar. Have fun!
    """
)

with st.sidebar:
    st.markdown(
        """
        <a href="https://ggiuliopirotta.github.io/">
            <button style="width:100%">Personal page 🧑‍💻</button>
        </a>
        """,
        unsafe_allow_html=True,
    )
