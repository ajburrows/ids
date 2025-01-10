import mysql.connector
import sql_config

db_config = {
    'host': sql_config.DB_HOST,
    'user': sql_config.DB_USER,
    'password': sql_config.DB_PASSWORD,
    'database': sql_config.DB_NAME
}

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

if __name__ == '__main__':
    clear_table()