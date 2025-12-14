import streamlit as st
import app.services.user_service as LoginRegister
import app.data.schema as Schema
import auth
import app.data.incidents as CyberFuncs
import app.data.datasets as dt
import app.data.tickets as tickets
def LoginCheck() -> None:
    """
    Checks if user has logged in through Login Page. Sets values to False/None if not
    """
    if "users" not in st.session_state:
        st.session_state.users = {}

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""


def ConfigLayout():
    """
    Configures page layout and creates tabs for login and register
    Returns: tab_login, tab_register: DeltaGenerator (Tabs)
    """
    st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")
    st.title("Welcome")
    tab_login, tab_register = st.tabs(["Login", "Register"])
    return tab_login, tab_register


def GoCyber() -> None:
    """
    Checks if user's logged in, if yes switches page to Cyber_Analytics.py
    Returns: None
    """
    if st.session_state.logged_in:
        st.success("Already logged in as **{}**.".format(st.session_state.username))
        
        if st.button("Go to Cyber Analytics Dashboard"):
            st.switch_page("pages/Cyber_Analytics.py")
            
        st.stop()  # Stop execution so login forms don't render


def Login(loginTab) -> None:
    """
    Explanation: 
        Creates textboxes for user input for username and password. 
        When button pressed, goes to user_service.py and checks if login is successful.
        If yes, goes to Cyber_Analytics
        
    Args:
        loginTab (_DeltaGenerator_): Tab in which login widgets go in
    """
    with loginTab:
        st.subheader("Login")

        loginUsername = st.text_input("Username", key="login_username")
        loginPasswd = st.text_input("Password", type="password", key="login_password")

        if st.button("Log in", type="primary"):
            # Tuple: (Success_Bool, Message_Str)
            loginSuccess = LoginRegister.LoginUser(loginUsername, loginPasswd)
            
            if loginSuccess[0]:
                st.session_state.logged_in = True
                st.session_state.username = loginUsername
                st.success("Welcome back, {}! ".format(loginUsername))

                # Redirect to dashboard page
                st.switch_page("pages/Cyber_Analytics.py")
            else:
                st.error(loginSuccess[1])


def Register(registerTab): 
    """
    Explanation:
        Gets user input through widgets for username, password, and confirm password
        Validates input through auth.py.
        If validated, registers through user_service.py.
    Args:
        registerTab (_DeltaGenerator_): Tab where registration widgets reside
    """
    with registerTab:
        st.subheader("Register")

        new_username = st.text_input("Choose a username", key="register_username")
        new_password = st.text_input("Choose a password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

        if st.button("Create account"):
            # 1. Check for empty fields first
            if not new_username or not new_password:
                st.warning("Please fill in all fields.")
                return # Stop here

            # 2. Run Validations
            checkValidName = auth.validate_username(new_username)
            checkValidPWrd = auth.validate_password(new_password, confirm_password)

            # 3. Handle Errors (Use elif to prioritize errors)
            if not checkValidName[0]:
                st.error(checkValidName[1])
            
            elif not checkValidPWrd[0]:
                st.error(checkValidPWrd[1])
            
            else:
                # 4. Only attempt registration if ALL validations pass
                checkRegister = LoginRegister.RegisterUser(new_username, new_password)
                
                if not checkRegister[0]: # Failure (e.g., User already exists)
                    st.error(checkRegister[1])
                else:
                    # Success
                    st.session_state.users[new_username] = new_password
                    st.success("Account created! You can now log in from the Login tab.")
                    st.info("Tip: go to the Login tab and sign in with your new account.")


if __name__ == "__main__": 
 
  
    Schema.create_all_tables()
    LoginCheck()
    GoCyber()
    
    logTab, regTab = ConfigLayout()
    Register(regTab)
    Login(logTab)