import smtplib
import streamlit as st


### ---------------------------------------------------------------------------------------------------- ###
### SEND


def send_email(sender, body):

    if sender == "" or body == "":
        st.warning("Sender or body are empty ❓")
        return
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login("gipopiro@gmail.com", "znsv hafk rijz xnmp")
        server.sendmail("gipopiro@gmail.com", "gipopiro@gmail.com", f"Subject: From {sender} via Streamlit\n\n{body}")
        server.quit()
    
        st.success("Email sent 🚀")
    except:
        st.error(f"Some error occurred 🚫")


### ---------------------------------------------------------------------------------------------------- ###
### PAGE MARKDOWN

    
st.markdown(
    '''
    # Send me a message 🦜

    ---

    Feel free to shoot me an email and I'll take a look 👀
    '''
)


### ---------------------------------------------------------------------------------------------------- ###
### INPUTS


col, _ = st.columns((0.4, 0.6))

with col:
    sender_ = st.text_input(
        label   = "From",
        value   = "Anonymus"
    )

body_ = st.text_area(
    label   = "Body",
    value   = ""
)

send_ = st.button(
    label       = "Send email",
    on_click    = send_email,
    args        = (sender_, body_)
)
