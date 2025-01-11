import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import sql_config

class TrafficViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Network Traffic Viewer')
        self.root.geometry('800x400')

        # Create the table
        self.tree = ttk.Treeview(root, columns=('id', 'timestamp', 'src_ip', 'src_port', 'dest_ip', 'dest_port', 'payload'),
                                 show='headings')
        self.tree.heading('id', text="ID")
        self.tree.heading('timestamp', text='Timestamp')
        self.tree.heading('src_ip', text='Source IP')
        self.tree.heading('src_port', text='Source Port')
        self.tree.heading('dest_ip', text='Dest IP')
        self.tree.heading('dest_port', text='Dest Port')
        self.tree.heading('payload', text='Payload')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Refresh button
        refresh_button = tk.Button(root, text='Refresh', command=self.load_data)
        refresh_button.pack(pady=10)

        # load initial data
        self.load_data()
    
    def connect_to_db(self):
        try:
            connection = mysql.connector.connect(
                host=sql_config.DB_HOST,
                user=sql_config.DB_USER,
                password=sql_config.DB_PASSWORD,
                database=sql_config.DB_NAME
            )
            return connection
        except Error as e:
            print(f'Error connecting to Traffic Server: {e}')
            return None
    
    def load_data(self):
        connection = self.connect_to_db()
        if connection is None:
            return
        
        cursor = connection.cursor()
        cursor.execute(f'SELECT * from traffic_logs')
        rows = cursor.fetchall()

        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for row in rows:
            self.tree.insert('', tk.END, values=row)

        connection.close()

if __name__ == '__main__':
    root = tk.Tk()
    app = TrafficViewerApp(root)
    root.mainloop()