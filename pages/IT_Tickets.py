import streamlit as st
import app.data.tickets as tickets
import plotly.express as exp
from openai import OpenAI
from datetime import datetime


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
    if 'itMsgs' not in st.session_state:
        st.session_state.itMsgs = [] 

    # 2. The Check
    if not st.session_state.logged_in:
        st.warning("Please log in to access the IT Tickets dashboard.")
        
        # 3. Navigation Button
        if st.button("Go to Login Page"):
            st.switch_page("home.py") 
        st.stop()

def selectcolumn():
    """
    Select a column from the IT tickets table for analysis.
    """
    st.divider()
    st.subheader("Select Column for Analysis")
    columns = ["subject", "priority", "status"]
    selected_column = st.selectbox("Select Column for Analysis", columns)
    return selected_column

def barchart(data, xAxis: str):
    """
    Create and display a bar chart using Plotly Express.
    """
    # Updated text to reflect IT Tickets context
    st.subheader("Breakdown of "+xAxis)

    # Updated title to match the dataset (assuming xAxis maps to subject/priority)
    fig = exp.bar(data, x=xAxis,y="COUNT(*)", title=xAxis+" Distribution")
    
    st.plotly_chart(fig)

def linechart(df):
    """
    Creates a line chart and Contains all the dates
    grouped by the no of records in each date.
    """
    st.subheader("Tickets Over Time")
    
    # Updated column to 'created_date'
    print(df)
    date_counts = df['created_date'].value_counts().sort_index()
    cntvalues= df['COUNT(*)'].values
    fig = exp.line(
        x=date_counts.index, 
        y=cntvalues, 
        labels={'x': 'Date', 'y': 'Number of Tickets'}, 
        title="Tickets Over Time"
    )
    st.plotly_chart(fig)

def piechart(column) -> None:
    """
    Creates a pie chart showing the distribution of ticket subjects.
    """
    st.subheader(column+" Distribution")
    
    # Use the updated function to get the dataframe
    data = tickets.get_all_tickets("",column)
    
    # 'subject' is the equivalent of 'incident_type' in the new CSV
    subject_counts = data[column].value_counts()
    cntvalues= data['COUNT(*)'].values   
    fig = exp.pie(
        values=cntvalues, 
        names=subject_counts.index, 
        title=column+" Distribution"
    )
    st.plotly_chart(fig)

def insertticket():
    """
    Collect ticket details from user input based on CSV values.
    """
    ticket_id = st.text_input("Ticket ID")
    
    subject_options = (
        "Software Installation Request", "Password Reset Request", 
        "VPN Connection Failed", "Mouse/Keyboard Malfunction", 
        "Laptop Screen Flickering", "Printer Jammed", 
        "Wi-Fi Access Issue", "Blue Screen Error", 
        "System Slow Performance", "Access to Shared Drive Denied", 
        "Monitor Display Issue", "Email Not Syncing"
    )
    subject = st.selectbox("Subject", subject_options)
    
    priority_options = ("Critical", "High", "Medium", "Low")
    priority = st.selectbox("Priority", priority_options)
    
    status_options = ("Closed", "In Progress", "Open", "Pending User Action", "Resolved")
    status = st.selectbox("Status", status_options)
    
    created_date = st.date_input("Date")
    
    created_at = datetime.combine(created_date, datetime.now().time())

    return ticket_id, subject, priority, status, str(created_date), str(created_at)

def updateticket():
    """
    Collect ticket details for updating from user input.
    """
    ticket_id = st.text_input("Ticket ID to Update")
    
    subject_options = (
        "Software Installation Request", "Password Reset Request", 
        "VPN Connection Failed", "Mouse/Keyboard Malfunction", 
        "Laptop Screen Flickering", "Printer Jammed", 
        "Wi-Fi Access Issue", "Blue Screen Error", 
        "System Slow Performance", "Access to Shared Drive Denied", 
        "Monitor Display Issue", "Email Not Syncing"
    )
    subject = st.selectbox("New Subject", subject_options)
    
    priority_options = ("Critical", "High", "Medium", "Low")
    priority = st.selectbox("New Priority", priority_options)
    
    status_options = ("Closed", "In Progress", "Open", "Pending User Action", "Resolved")
    status = st.selectbox("New Status", status_options)
    
    created_date = st.date_input("New Date")
    
    created_at = datetime.combine(created_date, datetime.now().time())

    return ticket_id, subject, priority, status, str(created_date), str(created_at)

def deleteticket():
    """
    Collect ticket ID for deletion from user input.
    """
    ticket_id = st.text_input("Ticket ID to Delete")
    return ticket_id

def crud(operation):
    """
    Read, Handle, Create, Update, or Delete operations for IT Tickets.
    """
    if operation =="Read":
        st.dataframe(tickets.get_tickets_dataframe(""))
    if operation == "Create":

        # Pass the tuple items directly to the insert function for tickets
        values = insertticket()
        if st.button('Create'):
            new_id = tickets.insert_ticket(values[0], values[1], values[2], values[3], values[4])
            st.success("IT Ticket '{}' logged successfully.".format(new_id))

    elif operation == "Update":
        # Pass the tuple items to the update function
        values = updateticket()
        if st.button('Update'):
            if tickets.update_ticket(values[0], values[1], values[2], values[3], values[4]):
                st.success("Ticket '{}' modified successfully.".format(values[0]))
            else:
                st.error("Unable to update ticket '{}'.".format(values[0]))

    elif operation == "Delete":
        values = deleteticket()
        if st.button('Delete'):
            if tickets.delete_ticket(values):
                st.success("Ticket '{}' deleted successfully.".format(values))
            else:
                st.error("Unable to delete ticket '{}'.".format(values))

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
    Display previous IT support messages from session state.
    """
    if 'itMsgs' in st.session_state:
        for msg in st.session_state.itMsgs:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

def AIAssistant():
    """
    Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("IT Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our IT expert (GPT 4.0mini)...")
    gptMsg = [{"role": "system", "content": "You are an IT expert, you hold knowledge specialising in office related IT incidents. Make sure your responses are not too long"}]
    if prompt:
        #Save user response
        st.session_state.itMsgs.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create( 
                model = "gpt-4o-mini",
                messages = gptMsg + st.session_state.itMsgs,
                stream = True,
            )
            
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)
        
        #Save AI response
        st.session_state.itMsgs.append({ "role": "assistant", "content": fullReply })

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
    st.title("IT Tickets Dashboard")
    analysis,crudop,ai = st.tabs(["Data Analysis","CRUD Operations","AI Assistant"])
    with analysis:
        st.subheader("IT Tickets Analysis Dashboard")
        column=selectcolumn()
        data=tickets.get_all_tickets("",column)
        barchart(data,column)
        piechart(column)
        linechart(tickets.get_all_tickets("","created_date"))
    with crudop:
        st.subheader("Manage IT Tickets")
        operation = st.selectbox("Select Operation", ["Read", "Create", "Update", "Delete"])
        crud(operation)
    with ai:
        st.subheader("IT Support AI Assistant")
        AIAssistant()
    st.divider()
    logout()       