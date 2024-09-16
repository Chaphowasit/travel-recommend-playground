# import os
# import json
# import pymysql
# from pymysql import OperationalError, ProgrammingError
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Database connection details from environment variables
# db_config = {
#     'host': os.getenv('DB_HOST'),
#     'user': os.getenv('DB_USER'),
#     'password': os.getenv('DB_PASSWORD'),
#     'database': os.getenv('DB_NAME')
# }

# def escape_string(value):
#     if isinstance(value, str):
#         return pymysql.converters.escape_string(value)
#     return value

# def infer_schema_from_json(data):
#     schema = {}
#     for entry in data:
#         for key, value in entry.items():
#             # Skip NoneType values
#             if value is None:
#                 continue
            
#             if key not in schema:
#                 if isinstance(value, int):
#                     schema[key] = 'INT'
#                 elif isinstance(value, float):
#                     schema[key] = 'DOUBLE'
#                 elif isinstance(value, bool):
#                     schema[key] = 'BOOLEAN'
#                 elif isinstance(value, str) and not key.endswith('_time'):
#                     if len(value) <= 255:
#                         schema[key] = 'VARCHAR(255)'
#                     else:
#                         schema[key] = 'TEXT'
#                 elif isinstance(value, str) and key.endswith('_time'):
#                     schema[key] = 'TIME'
#                 else:
#                     schema[key] = 'TEXT'
                    
#             else:
#                 if isinstance(value, str):
#                     if len(value) > 255:
#                         schema[key] = 'TEXT'
#                 if isinstance(value, int) and schema[key] != 'INT':
#                     schema[key] = 'INT'
#                 if isinstance(value, float) and schema[key] != 'DOUBLE':
#                     schema[key] = 'DOUBLE'
#                 if isinstance(value, bool) and schema[key] != 'BOOLEAN':
#                     schema[key] = 'BOOLEAN'
#     return schema


# def create_table_from_schema(connection, table_name, schema):
#     with connection.cursor() as cursor:
#         # Add the id column with appropriate format and set as primary key
#         fields = "`id` VARCHAR(5) PRIMARY KEY, " + ", ".join([f"`{col}` {dtype}" for col, dtype in schema.items()])
#         create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({fields}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
#         cursor.execute(create_table_query)
#         connection.commit()

# def insert_data_into_table(connection, table_name, data, schema):
#     with connection.cursor() as cursor:
#         # Determine the prefix for the ID based on the table name
#         if table_name == 'foodAndDrink_Detail':
#             prefix = 'F'
#         elif table_name == 'accommodation_Detail':
#             prefix = 'H'
#         elif table_name == 'activity_Detail':
#             prefix = 'A'
#         else:
#             raise ValueError("Unknown table name")

#         # Fetch the current max id to calculate the next one
#         cursor.execute(f"SELECT MAX(CAST(SUBSTRING(id, 2) AS UNSIGNED)) FROM `{table_name}`")
#         max_id = cursor.fetchone()[0]
#         next_id = (max_id + 1) if max_id else 1

#         for entry in data:
#             # Generate the new id
#             entry_id = f"{prefix}{str(next_id).zfill(4)}"
#             next_id += 1

#             columns = ", ".join([f"`{col}`" for col in schema.keys()])
#             placeholders = ", ".join(["%s"] * len(schema))
#             insert_query = f"INSERT INTO `{table_name}` (`id`, {columns}) VALUES (%s, {placeholders})"

#             # Prepare values based on their types
#             values = []
#             for col in schema.keys():
#                 value = entry.get(col, None)  # Get the value, or use None if not present
#                 if isinstance(value, str):
#                     value = escape_string(value)
#                 elif isinstance(value, (list, dict)):
#                     # Convert lists or dicts to JSON strings
#                     value = json.dumps(value)
#                 elif value is None:
#                     value = None  # This will be treated as NULL in SQL
#                 values.append(value)
#             try:
#                 cursor.execute(insert_query, [entry_id] + values)
#             except Exception as e:
#                 print(f"Error executing query: {e}")
#                 raise
#         connection.commit()

# def process_json_files(connection, json_directory, table_name):
#     json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]

#     for json_file in json_files:
#         input_file = os.path.join(json_directory, json_file)

#         with open(input_file, "r", encoding="utf-8") as file:
#             json_data = json.load(file)

#         if not json_data:
#             continue

#         schema = infer_schema_from_json(json_data)
#         create_table_from_schema(connection, table_name, schema)
#         print(f"Table '{table_name}' created")
#         insert_data_into_table(connection, table_name, json_data, schema)
#         print(f"Data from '{input_file}' inserted into '{table_name}'")

# def main():
#     try:
#         connection = pymysql.connect(**db_config)
#         process_json_files(connection, 'eat/extract_json', 'foodAndDrink_Detail')
#         # process_json_files(connection, 'stay/extract_json', 'accommodation_Detail')
#         # process_json_files(connection, 'do/extract_json', 'activity_Detail')
#     except OperationalError as e:
#         print(f"Error connecting to MariaDB: {e}")
#     except ProgrammingError as e:
#         print(f"SQL Error: {e}")
#     finally:
#         if connection:
#             connection.close()

# if __name__ == "__main__":
#     main()

import os
import json
import pymysql
from pymysql import OperationalError, ProgrammingError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details from environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def escape_string(value):
    if isinstance(value, str):
        return pymysql.converters.escape_string(value)
    return value


def infer_schema_from_json(data):
    schema = {}
    for entry in data:
        for key, value in entry.items():
            # Skip NoneType values
            if value is None:
                continue
            
            if key not in schema:
                if isinstance(value, int):
                    schema[key] = 'INT'
                elif isinstance(value, float):
                    schema[key] = 'DOUBLE'
                elif isinstance(value, bool):
                    schema[key] = 'BOOLEAN'
                elif isinstance(value, str) and not key.endswith('_time'):
                    if len(value) <= 255:
                        schema[key] = 'VARCHAR(255)'
                    else:
                        schema[key] = 'TEXT'
                elif isinstance(value, str) and key.endswith('_time'):
                    schema[key] = 'TIME'
                else:
                    schema[key] = 'TEXT'
                    
            else:
                if isinstance(value, str):
                    if len(value) > 255:
                        schema[key] = 'TEXT'
                if isinstance(value, int) and schema[key] != 'INT':
                    schema[key] = 'INT'
                if isinstance(value, float) and schema[key] != 'DOUBLE':
                    schema[key] = 'DOUBLE'
                if isinstance(value, bool) and schema[key] != 'BOOLEAN':
                    schema[key] = 'BOOLEAN'
    return schema

def create_table_from_schema(connection, table_name, schema):
    with connection.cursor() as cursor:
        fields = ", ".join([f"`{col}` {dtype}" for col, dtype in schema.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({fields}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        cursor.execute(create_table_query)
        connection.commit()

def insert_data_into_table(connection, table_name, data, schema):
    with connection.cursor() as cursor:
        for entry in data:
            columns = ", ".join([f"`{col}`" for col in schema.keys()])
            placeholders = ", ".join(["%s"] * len(schema))
            insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
            # Prepare values based on their types
            values = []
            for col in schema.keys():
                value = entry.get(col, None)  # Get the value, or use None if not present
                if isinstance(value, str):
                    value = escape_string(value)
                elif isinstance(value, (list, dict)):
                    # Convert lists or dicts to JSON strings
                    value = json.dumps(value)
                elif value is None:
                    value = None  # This will be treated as NULL in SQL
                values.append(value)
            print(f"Inserting: {values}")
            try:
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"Error executing query: {e}")
                raise
        connection.commit()

def process_json_files(connection, json_directory, table_name):
    json_files = [f for f in os.listdir(json_directory) if f.endswith(".json")]
    for json_file in json_files:
        input_file = os.path.join(json_directory, json_file)
        with open(input_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        if not json_data:
            continue
        schema = infer_schema_from_json(json_data)
        create_table_from_schema(connection, table_name, schema)
        print(f"Table '{table_name}' created")
        insert_data_into_table(connection, table_name, json_data, schema)
        print(f"Data from '{input_file}' inserted into '{table_name}'")

def main():
    try:
        connection = pymysql.connect(**db_config)
        process_json_files(connection, 'eat/extract_json', 'foodAndDrink')
        process_json_files(connection, 'stay/extract_json', 'accommodation')
        process_json_files(connection, 'do/extract_json', 'activity')
    except OperationalError as e:
        print(f"Error connecting to MariaDB: {e}")
    except ProgrammingError as e:
        print(f"SQL Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()
