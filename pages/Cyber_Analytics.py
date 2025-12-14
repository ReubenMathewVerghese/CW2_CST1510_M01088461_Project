import streamlit as st
from openai import OpenAI
import plotly.express as exp
import app.data.incidents as CyberFuncs

def debug(*args):
    """
    Debugging function to print arguments to console.
    """
    for arg in args:
        print("DEBUG: {}".format(arg)) 

def check_login():
    """
    Check if user is logged in and handle redirection.
    """
    # 1. Initialize Default State
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'cyberMsgs' not in st.session_state:
        st.session_state.cyberMsgs = [] 

    # 2. The Check
    if not st.session_state.logged_in:
        st.warning("Please log in to access the Cyber Analytics dashboard.")
        
        # 3. Navigation Button
        if st.button("Go to Login Page"):
            st.switch_page("home.py") 
            
        st.stop()

def selectcolumn():
    """
    Select a column from the cyber incidents table for analysis.
    """
    st.divider()
    st.subheader("Select Column for Analysis")
    columns = ["incident_type", "severity", "status"]
    selected_column = st.selectbox("Select Column for Analysis", columns)
    return selected_column

def barchart(data, xAxis: str):
    """
    Create and display a bar chart using Plotly Express.
    """
    st.subheader("Breakdown of"+" "+xAxis)

    fig = exp.bar(data, x=xAxis,y="COUNT(*)",title=xAxis+" Distribution")
    
    st.plotly_chart(fig)

def linechart(df):
    """
    Creates a line chart and Contains all the dates
    grouped by the no of records in each date.
    """
    st.subheader("Incidents Over Time")
    date_counts = df['date'].value_counts().sort_index()
    cntvalues = df['COUNT(*)'].values
    fig = exp.line(x=date_counts.index, y=cntvalues, labels={'x': 'Date', 'y': 'Number of Incidents'}, title="Incidents Over Time")
    st.plotly_chart(fig)

def piechart(column)->None:
    """
    Creates a pie chart showing the distribution of incident types.
    """
    st.subheader(column+" Distribution")
    data = CyberFuncs.get_all_incidents("",column)
    incident_counts = data[column].value_counts()
    cntvalues = data['COUNT(*)'].values
    fig = exp.pie(values=cntvalues, names=incident_counts.index, title=column+" Distribution")
    st.plotly_chart(fig)

def insertincident():
    """
    Collect incident details from user input.
    """
    tId = st.text_input("Ticket ID")
    incidentType = st.selectbox("Incident Type", ("Brute Force", "DDoS", "Data Leak", "Insider Threat", 
                                 "Malware", "Phishing", "Ransomware", "SQL Injection"))
    date = str(st.date_input("Date"))
    severity = st.selectbox("Severity", ("Critical", "High", "Low", "Medium"))
    status = st.selectbox("Status", ("Closed", "Open", "Pending Review", "Resolved", "Under Investigation"))
    
    return tId, incidentType, severity, status, date

def updateincident():
    """
    Collect incident details for updating from user input.
    """
    tId = st.text_input("Ticket ID to Update")
    incidentType = st.selectbox("New Incident Type", ("Brute Force", "DDoS", "Data Leak", "Insider Threat", 
                                 "Malware", "Phishing", "Ransomware", "SQL Injection"))
    date = str(st.date_input("New Date"))
    severity = st.selectbox("New Severity", ("Critical", "High", "Low", "Medium"))
    status = st.selectbox("New Status", ("Closed", "Open", "Pending Review", "Resolved", "Under Investigation"))
    
    return tId, incidentType, severity, status, date

def deleteincident():
    """
    Collect incident ID for deletion from user input.
    """
    tId = st.text_input("Ticket ID to Delete")
    return tId

def crud(operation):
    """
    Read, Handle, Create, Update, or Delete operations for Cyber Security Incidents.
    """
    if operation =="Read":
        st.dataframe(CyberFuncs.get_dataframequery(""))
    if operation == "Create":

        # Pass the tuple items directly to the insert function for incidents
        values = insertincident()
        if st.button('Create'):
            new_id = CyberFuncs.insert_incident(int(values[0]), values[1], values[2], values[3],values[4]) 
            st.success("Cyber Incident '{}' logged successfully.".format(new_id))

    elif operation == "Update":
        # Pass the tuple items to the update function
        values = updateincident()
        if st.button('Update'):
            if CyberFuncs.update_incident(int(values[0]), values[1], values[2], values[3], values[4]):
                st.success("Incident '{}' modified successfully.")
            else:
                st.error("Unable to update incident '{}'.")

    elif operation == "Delete":
        values = deleteincident()
        if st.button('Delete'):
                if CyberFuncs.delete_incident(int(values)):
                    st.success("Incident '{}' removed from database.".format(values))
                else:
                    st.error("Unable to delete incident '{}'.".format(values))

def Streaming(completion):
    """
        Explanation: Takes delta time and displays ChatGPT response in small chunks
    """
    container = st.empty()
    fullReply = ""
    
    for chunk in completion:
        delta = chunk.choices[0].delta
        if delta.content:
            fullReply += delta.content
            container.markdown(fullReply + "▌") # Add cursor effect, character is "Left Hand Block"
    
    # Remove cursor and show final response
    container.markdown(fullReply)
    return fullReply

def DisplayPrevMsgs():
    """
        Displays all messages in st.session_state.cyberMsgs except for messages by system 
        System message is initial prompt given to gpt for it to know its specific role
    """
    for message in st.session_state.cyberMsgs:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def AIAssistant():
    """
        Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("IT Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our IT expert (GPT 4.0mini)...")
    gptMsg = [{"role": "system", "content": "You are an expert in office related cyber incidents. Make sure your responses are not too long"}]
    if prompt:
        #Save user response
        st.session_state.cyberMsgs.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create( 
                model = "gpt-4o-mini",
                messages = gptMsg + st.session_state.cyberMsgs,
                stream = True,
            )
            
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)
        
        #Save AI response
        st.session_state.cyberMsgs.append({ "role": "assistant", "content": fullReply })

def logout():
    """
    Log out the current user and redirect to the login page.
    """
    st.divider()
    if st.button("Log Out", type="primary"):
    # 1. Clear session state
        st.session_state.logged_in = False
        st.session_state.username = "" 
    
    # 2. Redirect immediately
        st.switch_page("home.py")

if __name__ == "__main__":
    client = OpenAI(api_key = st.secrets['OPENAI_API_KEY'])


    check_login()
    st.title("Data Analysis")
    analysis,crudop,ai=st.tabs(["Data Analysis","CRUD Operations","AI Assistant"])
    with analysis:
        st.subheader("Cyber Security Incidents Analysis Dashboard")
        column=selectcolumn()
        data = CyberFuncs.get_all_incidents("",column)
        print(data)
        barchart(data, column)
        piechart(column)
        linechart(CyberFuncs.get_all_incidents("", "date"))
        
    with crudop:
        st.subheader("Cyber Security Incidents - CRUD Operations")
        option=st.selectbox("Select Operation", ("Read","Create", "Update", "Delete"), key="cud_select")
        crud(option)
        
    with ai:
        st.subheader("AI Assistant for Cyber Security Incidents")
        AIAssistant()
    st.divider()
    logout()