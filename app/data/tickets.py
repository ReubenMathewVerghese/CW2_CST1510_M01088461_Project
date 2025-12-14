import csv
from pathlib import Path
import pandas as pd 
from app.data.db import connect_database

def insert_ticket(ticket_id, subject, priority, status, created_date):
    """
    Adds a new ticket record to the database matching the CSV structure.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = """
        INSERT INTO IT_Tickets 
        (ticket_id, subject, priority, status, created_date)
        VALUES (?, ?, ?, ?, ?)
    """
    values = (ticket_id, subject, priority, status, created_date)
    
    cursor.execute(sql, values)
    db.commit()
    db.close()

def drop_tickets_table():
    """
    Drops the IT_Tickets table from the database.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = "DROP TABLE IF EXISTS IT_Tickets"
    
    cursor.execute(sql)
    db.commit()
    db.close()

def update_ticket(ticket_id, subject, priority, status, created_date):
    """
    Updates an existing ticket record in the database.
    Returns True if successful, False otherwise.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = """
        UPDATE IT_Tickets
        SET subject = ?, priority = ?, status = ?, created_date = ?
        WHERE ticket_id = ?
    """
    # The ticket_id goes last to match the WHERE clause
    values = (subject, priority, status, created_date, ticket_id)
    
    cursor.execute(sql, values)
    db.commit()

    # 3. Check if any row was updated
    success = cursor.rowcount > 0
    
    db.close()
    return success

def delete_ticket(ticket_id):
    """
    Deletes a ticket record from the database by its ticket_id.
    Returns True if successful, False otherwise.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = "DELETE FROM IT_Tickets WHERE ticket_id = ?"
    cursor.execute(sql, (ticket_id,))
    db.commit()

    # 3. Check if any row was deleted
    success = cursor.rowcount > 0
    
    db.close()
    return success

def get_groupby(column):
    """
    Retrieves distinct values for a specified column from the IT_Tickets table.
    """
    # 1. Establish connection
    db = connect_database()
    
    # 2. Generate the full SQL command
    sql_command = f"SELECT {column},COUNT(*) FROM IT_Tickets GROUP BY {column}"
    
    # 3. Execute query and load directly into a Pandas DataFrame
    results_df = pd.read_sql_query(sql_command, db)
    print(results_df)
    
    # 4. Close connection and return data
    db.close()
    return results_df

def get_all_tickets(filter_str,column):
    """
    Retrieves ticket records from the database and returns them as a DataFrame.
    Applies the provided SQL filter string to refine the results.
    """
    # 1. Establish connection
    db = connect_database()
    
    # 2. Generate the full SQL command using the helper function
    # Renamed to match the IT tickets context
    sql_command =f"SELECT {column},COUNT(*) FROM IT_Tickets GROUP BY {column}"
    
    # 3. Execute query and load directly into a Pandas DataFrame
    results_df = pd.read_sql_query(sql_command, db)
    print(results_df)
    
    # 4. Close connection and return data
    db.close()
    return results_df

def get_tickets_dataframe(filter_str=None):
    """
    Returns the DataFrame for IT_Tickets table.
    """
    # 1. Establish connection
    db = connect_database()
    
    # 2. Generate the full SQL command
    sql_command = "SELECT * FROM IT_Tickets"

    # 3. Execute query and load directly into a Pandas DataFrame
    results_df = pd.read_sql_query(sql_command, db)
    print(results_df)
    
    # 4. Close connection and return data
    db.close()
    return results_df

def get_ticketquery(filter_str,column):
    """
    Constructs the SQL query string for retrieving tickets with an optional filter.
    """
    # 1. Define the base requirement
    query = f"SELECT {column},COUNT(*) FROM IT_Tickets GROUP BY {column}"
    
    # 2. Add the condition if it exists
    if filter_str:
        query += f" WHERE {filter_str}"
    print('Filter string 1',filter_str)
    
    return query

def total_tickets(filter_str: str) -> int:
    """
    Executes the query with the optional filter and returns the total count of matches
    in the it_tickets table.
    """
    # 1. Open Connection
    conn = connect_database()
    
    # 2. Get the SQL string using the helper function we updated earlier
    sql_cmd = get_all_tickets(filter_str)
    
    # 3. Load results into a DataFrame
    df_results = pd.read_sql_query(sql_cmd, conn)
    
    conn.close()
    
    # 4. Return the number of rows found
    return len(df_results)

def transfer_csv():
    import csv
    from pathlib import Path
    
    conn = connect_database()
    cursor = conn.cursor()
    
    # Updated to read from the correct file 'it_tickets.csv'
    with open(Path("DATA/it_tickets.csv")) as csv_file:
        reader = csv.reader(csv_file)
                    
        # Skip the header row
        next(reader)
        
        for row in reader:
            cursor.execute("""
                INSERT INTO IT_Tickets 
                (ticket_id, subject, priority, status, created_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row[0], row[1], row[2], row[3], row[4], row[5]))
            
    conn.commit()
    conn.close()
