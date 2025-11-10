"""
Connects to PostgreSQL database
"""

import os
import psycopg2
import platform
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from cryptography.fernet import Fernet
from dataclasses import dataclass




@dataclass
class Connect:
    """
    Establish a connection to a PostgreSQL database.

    This class provides a convenient way to connect to a PostgreSQL server using
    either direct parameters or environment variables. If connection parameters
    are not provided explicitly, the following environment variables are used as
    fallbacks:

    - `PG_HOST` → server hostname  
    - `PG_PORT` → server port  
    - `PG_DB` → database name  
    - `PG_USER` → database username  
    - `PG_PASSWD` → user password  

    Parameters
    ----------
    host : str, optional
        Database server hostname. Defaults to the value of `PG_HOST` if unset.
    port : int or str, optional
        Database server port. Defaults to the value of `PG_PORT` if unset.
    db : str, optional
        Database name to connect to. Defaults to the value of `PG_DB` if unset.
    user : str, optional
        Username for authentication. Defaults to the value of `PG_USER` if unset.
    password : str, optional
        Password for authentication. Defaults to the value of `PG_PASSWD` if unset.
    schema : str, optional
        Target schema name within the database.
    table : str, optional
        Default table name to operate on.

    Examples
    --------
    Connect using explicit parameters:
        >>> db = pyconnpg.Connect(
                host='localhost',
                db='my_database',
                user='my_user',
                password='my_password',
            )
            

    Connect using environment variables:
        >>> db = pyconnpg.Connect()

    Connect to a specific schema and table:
        >>> db = pyconnpg.Connect(schema='analytics', table='users')
    """

    host: str = None
    port: int = None
    db: str = None
    user: str = None
    password: str = None
    schema: str = None
    table: str = None
        
        
    def __post_init__(self) -> None:
        # Load environment variables from $HOME/.pgenv
        if platform.system() == "Windows":
            home_dir = os.getenv('HOMEPATH')
        elif platform.system() == 'Linux':
            home_dir = os.getenv('HOME')
        else:
            raise FileNotFoundError('Home directory not found.')

        env_file = os.path.join(home_dir, '.pgenv')
        if os.path.isfile(env_file):
            load_dotenv(env_file)
            
        # Env fallback
        self.host = self.host or os.getenv('PG_HOST')
        self.port = self.port or os.getenv('PG_PORT')
        self.db = self.db or os.getenv('PG_DB')
        self.user = self.user or os.getenv('PG_USER')
        self.password = self.password or os.getenv('PG_PASSWD')

        try:
            if '=@' in self.password:
                key, passwd = self.password.split('@')
                cipher_suite = Fernet(key)
                self.password = cipher_suite.decrypt(passwd).decode()
        except TypeError:
            pass
                
        # Create connection to postgres
        self.conn = psycopg2.connect(host = self.host,
                                    port = self.port,
                                    database = self.db,
                                    user = self.user,
                                    password = self.password)
        self.cursor = self.conn.cursor()

    
    @property
    def version(self) -> str:
        """
        Returns:
            str: Postgres version
        """
        self.cursor.execute('SELECT VERSION()')
        result = self.cursor.fetchone()[0]
        return result
    

    def check_exists(self,column_name: str, find) -> bool:
        """
        Return True if it exists and False if not.
        column_name: where to find
        find: string or charater to find
        """
        query = f"select exists(select 1 from {self.schema}.{self.table} where {column_name}='{find}')"
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()[0]
        return result
    
    def check_exists_long(self,where: str) -> bool:
        """
        Return True if it exists and False if not.
        where: multiple where and/or clause
        """
        query = f"select exists(select 1 from {self.schema}.{self.table} where {where})"
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()[0]
        return result
    
    
    def insert(self, **kwargs):
        """
        Input (table_column_name=value) to insert.
        Note: column names should NOT be enclosed with quotes
        

        Ex. db.insert(product='ProductName', version=3)
        """
        columns = []
        values = []
        for column, value in kwargs.items():
            columns.append(column)
            values.append(value)

        # Remove quotations from column names
        # because it will cause an error during insert
        columns = ', '.join(columns)

        # Execute insert
        if len(values) == 1:
            # only one element to insert
            # using tuple with one element will cause an error due to comma - ('test',)
            self.cursor.execute(f"INSERT INTO {self.schema}.{self.table} ({columns}) VALUES (%s)",
                                (values[0],))

        else:
            # Inserting more than one values
            placeholders = ', '.join(['%s'] * len(values))
            self.cursor.execute(f"INSERT INTO {self.schema}.{self.table} \
                            ({columns}) VALUES ({placeholders})",
                            values)
            
        self.conn.commit()
        

    def batch_insert(self, data:list[dict]) -> bool:
        """
        Batch insert for PostgreSQL using "execute_values".
        Expects data like:
            [
                {"id": "2025-10-21_1", "date": "2025-10-21", "users": "user1", "usage": 3},
                {"id": "2025-10-21_2", "date": "2025-10-21", "users": "user2", "usage": 5},
            ]
           
        Example: Add dict records to list 
        records_to_insert = []
        for count, (user, usage) in enumerate(checkout_users.items(), start=1):
            record = {
                "id": f"{DT_UTC}_{count}",
                "date": DT_UTC,
                "users": user,
                "usage": usage,
                "check_conflict": "id"
            }
            records_to_insert.append(record)    
            
            
        Returns True when successful else False    
        """
        # Extract column names from first record
        if len(data) == 0:
            return False
        columns = data[0].keys()
        col_names = ', '.join(columns)

        # Convert list of dicts -> list of tuples (values only)
        values = [tuple(record[col] for col in columns) for record in data]
        
        # Build SQL statement
        sql = f"""
            INSERT INTO {self.schema}.{self.table} ({col_names})
            VALUES %s
        """
        
        # Execute batch insert
        execute_values(self.cursor, sql, values)
        self.conn.commit()
        
        return True
            


    def insert_many(self, data:list[dict]) -> bool:
        """
        Batch insert for PostgreSQL.
        Expects data like:
            [
                {"id": "2025-10-21_1", "date": "2025-10-21", "users": "user1", "usage": 3},
                {"id": "2025-10-21_2", "date": "2025-10-21", "users": "user2", "usage": 5},
            ]
           
        Example: Add dict records to list 
        records_to_insert = []
        for count, (user, usage) in enumerate(checkout_users.items(), start=1):
            record = {
                "id": f"{DT_UTC}_{count}",
                "date": DT_UTC,
                "users": user,
                "usage": usage,
                "check_conflict": "id"
            }
            records_to_insert.append(record)    
            
        """

        # Extract column names from first record
        if len(data) == 0:
            return False
        columns = data[0].keys()
        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join(columns)

        # Convert list of dicts -> list of tuples (values only)
        values = [tuple(record[col] for col in columns) for record in data]
        
        # Build SQL statement
        sql = f"""
            INSERT INTO {self.schema}.{self.table} ({col_names})
            VALUES ({placeholders})
        """
        
        # Execute batch insert
        self.cursor.executemany(sql, values)
        self.conn.commit()
        return True
        
    def insert_with_conflict_check(self, check_conflict, **kwargs):
        """
        Input (table_column_name=value) to insert.
        Note: column names should not be enclosed in quotes
        param: check_conflict is the name of the primary key column name

        Ex. db.insert_with_conflict_check(check_conflict='column_pkey', product='Versionvault', version=3)
        """
        columns = []
        values = []
        for column, value in kwargs.items():
            columns.append(column)
            values.append(value)

        # Remove quotations from column names
        # because it will cause an error during insert
        columns = ', '.join(columns)
        
        # Execute insert
        if len(values) == 1:
            # only one element to insert
            # using tuple with one element will cause an error due to comma - ('test',)
            self.cursor.execute(f"INSERT INTO {self.schema}.{self.table} ({columns}) \
                VALUES (%s) ON CONFLICT ({check_conflict}) DO NOTHING",
                (values[0],))

        else:
            # Inserting more than one values
            placeholders = ', '.join(['%s'] * len(values))
            self.cursor.execute(f"INSERT INTO {self.schema}.{self.table} ({columns}) \
                VALUES ({placeholders}) ON CONFLICT ({check_conflict}) DO NOTHING", values)
            
        self.conn.commit()
    
    
    def update_row(self, column_name: str, value, where: str):
        """
        Update the specific column data where the specified column exists
        column_name: column name to update
        value: value to insert/update in column. String must enclose with ''
        where: specify which specific row. Ex. id=1
        """
        self.cursor.execute(f"UPDATE {self.schema}.{self.table} SET {column_name}='{value}' WHERE {where}")
        self.conn.commit()


    def add_column(self, column_name: str, col_type: str):
        """
        Add a new column into the table.
        column_name: column name to add
        type: type of column. Ex. varchar, integer or date
        """
        self.cursor.execute(f"ALTER TABLE {self.schema}.{self.table} ADD COLUMN IF NOT EXISTS {column_name} {col_type}")
        self.conn.commit()


    def get_value_match(self, column_name: str, where_column: str, match: str) -> str:
        """
        Return the column name value of the where_column query is match.

        """
        self.cursor.execute(f"Select {column_name} from {self.schema}.{self.table} where {where_column}='{match}'")
        value = self.cursor.fetchone()[0]
        return value
    
    
    def delete_row(self, condition: str):
        """
        Delete rows based on condition.

        DELETE FROM {self.schema}.{self.table} WHERE {condition}
        """
        self.cursor.execute(f"DELETE FROM {self.schema}.{self.table} WHERE {condition}")
        self.conn.commit()


    def close(self) -> None:
        """
        Close the connection
        """
        self.conn.close()
        