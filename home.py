from kuhn_st import init_state
import streamlit as st


### -------------------------------------------------- ###
### --- PAGE MARKDOWN -------------------------------- ###


st.set_page_config(
    page_title="Giulio's web app"
)


init_state()


# Welcome message
st.markdown(
    '''
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
    '''
)

with st.sidebar:
    my_page_ = st.button("Personal page 🧑‍💻")