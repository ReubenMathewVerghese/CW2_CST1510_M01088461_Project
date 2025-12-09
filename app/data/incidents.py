import pandas as pd
from app.data.db import connect_database

def insert_incidents(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id

def get_all_incidents():
    """Get all incidents as DataFrame."""
    """
        Get all incidents as DataFrame.
        Takes filter: str as parameter and filters incidents
    """
    conn = connect_database()
    query = get_incidents_query(filter)
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_incidents_query(filter):
    """
        Returns query with filter if filter exist
    """
    if filter:
        return f"SELECT incident_type FROM cyber_incidents WHERE {filter}"
    
    return "SELECT incident_type FROM cyber_incidents"

def total_incidents(filter: str) -> int:
    conn = connect_database()
    query = get_incidents_query(filter)
    totalInc = pd.read_sql_query(query, conn)
    
    return len(totalInc)

def transfer_csv():
    import csv
    from pathlib import Path
    conn = connect_database()
    cursor = conn.cursor()
    with open(Path("DATA/cyber_incidents.csv")) as itFile:
        reader = csv.reader(itFile)
        header: bool = True
        for row in reader:
            if header:
                header = False
                continue
            cursor.execute("""
                INSERT INTO cyber_incidents 
                (date, incident_type, severity, status, description, reported_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row[0], row[1], row[2], row[3], row[4], row[5]))
    conn.commit()
    conn.close()