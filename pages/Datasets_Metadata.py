import streamlit as st
import app.data.datasets as dt
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
    if 'dtMsgs' not in st.session_state:
        st.session_state.dtMsgs = [] 

    # 2. The Check
    if not st.session_state.logged_in:
        st.warning("Please log in to access the Dataset Metadata dashboard.")
        
        # 3. Navigation Button
        if st.button("Go to Login Page"):
            st.switch_page("home.py") 
        st.stop()

def selectcolumn():
    """
    Select a column from the datasets metadata table for analysis.
    """
    st.divider()
    st.subheader("Select Column for Analysis")
    
    # Updated columns to match dt_metadata.csv
    columns = [ "category"]
    
    selected_column = st.selectbox("Select Column for Analysis", columns)
    return selected_column

def barchart(data, xAxis: str):
    """
    Create and display a bar chart using Plotly Express.
    """
    st.subheader("Breakdown of Datasets")

    fig = exp.bar(data, x=xAxis,y="COUNT(*)",title="Datasets Distribution")
    
    st.plotly_chart(fig)

def piechart(column)->None:
    """
    Create and display a pie chart using Plotly Express.
    """
    st.subheader("Datasets Distribution Pie Chart")

    # Fetch data for pie chart
    data = dt.get_all_metadata("", column)
    subcount=data[column].value_counts()
    cntvalues = data['COUNT(*)'].values
    fig = exp.pie(values=cntvalues,names=subcount.index, title="Datasets Distribution by {}".format(column))
    st.plotly_chart(fig)

def insertmetadata():
    """
    Collect dataset details from user input based on CSV values.
    """
    dataset_name = st.text_input("Dataset Name")
    
    category_options = (
        "Finance", "Healthcare", "Human Resources", 
        "IT Security", "Logistics", "Marketing", 
        "Operations", "Sales"
    )
    category = st.selectbox("Category", category_options)
    
    file_size_mb = st.number_input("File Size (MB)", min_value=0.0, format="%.2f")
    
    created_date = st.date_input("Date")
    
    created_at = datetime.combine(created_date, datetime.now().time())

    return dataset_name, category, file_size_mb, str(created_at)

def updatemetadata():
    """
    Collect dataset details from user input for updating records.
    """
    dataset_id = st.number_input("Dataset ID", min_value=1, step=1)
    dataset_name = st.text_input("Dataset Name")
    
    category_options = (
        "Finance", "Healthcare", "Human Resources", 
        "IT Security", "Logistics", "Marketing", 
        "Operations", "Sales"
    )
    category = st.selectbox("Category", category_options)
    
    file_size_mb = st.number_input("File Size (MB)", min_value=0.0, format="%.2f")
    
    created_date = st.date_input("Date")
    
    created_at = datetime.combine(created_date, datetime.now().time())

    return dataset_id, dataset_name, category, file_size_mb, str(created_at)

def deletemetadata():
    """
    Collect dataset name for deletion.
    """
    dataset_id = st.number_input("Dataset id to Delete")
    return dataset_id

def crud(operation):
    """
    Read, Handle, Create, Update, or Delete operations for Dataset Metadata.
    """
    if operation =="Read":
        st.dataframe(dt.get_metadata_dataframe(""))
    if operation == "Create":

        # Pass the tuple items directly to the insert function for metadata
        values = insertmetadata()
        if st.button('Create'):
            new_id = dt.insert_metadata(values[0], values[1], values[2]) 
            st.success("Dataset Metadata '{}' logged successfully.".format(new_id))

    elif operation == "Update":
        # Pass the tuple items to the update function
        values = updatemetadata()
        if st.button('Update'):
            if dt.update_metadata(values[0], values[1], values[2], values[3]):
                st.success("Dataset Metadata '{}' modified successfully.".format(values[0]))
            else:
                st.error("Unable to update Dataset Metadata '{}'.".format(values[0]))

    elif operation == "Delete":
        dataset_name = deletemetadata()
        if st.button('Delete'):
            if dt.delete_metadata(dataset_name):
                st.success("Dataset Metadata '{}' deleted successfully.".format(dataset_name))
            else:
                st.error("Unable to delete Dataset Metadata '{}'.".format(dataset_name))

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

    if 'itMsgs' in st.session_state:
        for msg in st.session_state.dtMsgs:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

def AIAssistant():
    """
    Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("IT Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our data expert (GPT 4.0mini)...")
    gptMsg = [{"role": "system", "content": "You are a data expert, you hold knowledge specialising in dataset metadata and analysis. Make sure your responses are not too long"}]
    if prompt:
        #Save user response
        st.session_state.dtMsgs.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create( 
                model = "gpt-4o-mini",
                messages = gptMsg + st.session_state.dtMsgs,
                stream = True,
            )
            
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)
        
        #Save AI response
        st.session_state.dtMsgs.append({ "role": "assistant", "content": fullReply })

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
    st.title("Dataset Metadata Dashboard")
    analysis,crudop,ai = st.tabs(["Data Analysis","CRUD Operations","AI Assistant"])
    with analysis:
        st.subheader("Datasets Metadata Analysis Dashboard")
        column=selectcolumn()
        data=dt.get_all_metadata("",column)
        barchart(data,column)
        piechart(column)
    with crudop:
        st.subheader("Manage Dataset Metadata")
        operation = st.selectbox("Select Operation", ["Read", "Create", "Update", "Delete"])
        crud(operation)
    with ai:
        st.subheader("Dataset Metadata AI Assistant")
        AIAssistant()
    st.divider()
    logout()
