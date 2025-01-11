import mysql.connector
import sql_config
import os

LOG_FILE_PATH = 'traffic.log'
db_config = {
    'host': sql_config.DB_HOST,
    'user': sql_config.DB_USER,
    'password': sql_config.DB_PASSWORD,
    'database': sql_config.DB_NAME
}

# delete all entries in the traffic_db table in the local MySQL database.
def clear_table():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        truncate_query = 'TRUNCATE TABLE traffic_logs'
        cursor.execute(truncate_query)
        conn.commit()
        print('All data has been cleared from traffic_logs')
    except mysql.connector.Error as e:
        print(f'Error: {e}')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print('MySQL connection closed.')

# delete all entries in traffic.log
def clear_log_file():
    try:
        with open(LOG_FILE_PATH, 'w') as file:
            file.write("")
        print(f'{LOG_FILE_PATH} has been wiped')
    except OSError as e:
        print(f'Error clearing log file: {e}')

if __name__ == '__main__':
    clear_table()
    clear_log_file()