import csv
from pathlib import Path
import pandas as pd 
from app.data.db import connect_database

def insert_metadata(dataset_name, category, file_size_mb):
    """
    Adds a new dataset metadata record to the database.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = """
        INSERT INTO Datasets_Metadata 
        (dataset_name, category, file_size_mb)
        VALUES (?, ?, ?)
    """
    values = (dataset_name, category, file_size_mb)
    
    cursor.execute(sql, values)
    db.commit()
    db.close()

def update_metadata(id, dataset_name, category, file_size_mb):
    """
    Updates an existing dataset metadata record in the database.
    Returns True if successful, False otherwise.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = """
        UPDATE Datasets_Metadata
        SET dataset_name = ?, category = ?, file_size_mb = ?
        WHERE id = ?
    """
    values = (dataset_name, category, file_size_mb, id)
    
    cursor.execute(sql, values)
    db.commit()

    # 3. Check if any row was updated
    success = cursor.rowcount > 0
    
    db.close()
    return success

def delete_metadata(id):
    """
    Deletes a dataset metadata record from the database by its ID.
    Returns True if successful, False otherwise.
    """
    # 1. Connect to the DB
    db = connect_database()
    cursor = db.cursor()

    # 2. Run the SQL Command
    sql = "DELETE FROM Datasets_Metadata WHERE id = ?"
    cursor.execute(sql, (id,))
    db.commit()

    # 3. Check if any row was deleted
    success = cursor.rowcount > 0
    
    db.close()
    return success

def drop_datasets_metadata_table():
    """
    Drops the Datasets_Metadata table from the database.
    """
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Datasets_Metadata")
    db.commit()
    db.close()

def get_groupby(column):
    """
    Retrieves distinct values for a specified column from the Datasets_Metadata table.
    Returns a list of distinct values.
    """
    db= connect_database()
    sql_command = f"SELECT {column}, COUNT(*) as count FROM Datasets_Metadata GROUP BY {column}"
    df = pd.read_sql_query(sql_command, db)
    db.close()
    return df

def get_all_metadata(filter_str,column):
    """
    Retrieves ticket records from the database and returns them as a DataFrame.
    Applies the provided SQL filter string to refine the results.
    """
    db=connect_database()
    sql_command =f"SELECT {column},COUNT(*) FROM Datasets_Metadata GROUP BY {column}"
    df = pd.read_sql_query(sql_command, db)
    db.close()
    return df

def get_metadata_dataframe(filter_str):
    """
    Retrieves dataset metadata records from the database and returns them as a DataFrame.
    Applies the provided SQL filter string to refine the results.
    """
    db = connect_database()
    sql_command = "SELECT * FROM Datasets_Metadata"
    df= pd.read_sql_query(sql_command, db)
    db.close()
    return df

def get_metadataquery(filter_str,column):
    """
    Constructs the SQL query string for retrieving tickets with an optional filter.
    """
    query = f"SELECT {column},COUNT(*) FROM Datasets_Metadata GROUP BY {column}"
    if filter_str:
        query += f" WHERE {filter_str}"
    return query

def total_metadata(filter_str):
    """
    Executes the query with the optional filter and returns the total count of matches
    in the it_tickets table.
    """
    conn= connect_database()
    sqlcmd = get_all_metadata(filter_str)
    df_results = pd.read_sql_query(sqlcmd, conn)
    conn.close()
    return len(df_results)

def transfer_csv():
    import csv
    from pathlib import Path
    
    conn = connect_database()
    cursor = conn.cursor()
    
    # Updated to read from the correct file 'datasets_metadata.csv'
    # Note: Adjust the path "DATA/" if your file is in a specific folder
    with open(Path("DATA/datasets_metadata.csv")) as csv_file:
        reader = csv.reader(csv_file)
                    
        # Skip the header row
        next(reader)
        
        for row in reader:
            cursor.execute("""
                INSERT INTO datasets_metadata 
                (dataset_name, category, file_size_mb, created_at)
                VALUES (?, ?, ?, ?)
            """, (row[0], row[1], row[2], row[3]))
            
    conn.commit()
    conn.close()

