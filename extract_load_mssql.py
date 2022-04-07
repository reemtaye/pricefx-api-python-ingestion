"""
Extracting data from the PFX API.
"""
import configparser
import base64
import json
# import sys
import requests
import pandas as pd
from sqlalchemy import create_engine

# def usage():
#     """Error message appears when arguments are missing"""
#     print('\nMissing an argument.  Usage:\n')
#     print('$ file_name.py <partition> e.g. main.py "prod" ')
#     sys.exit()


def b64_auth_header(env_partition, uid,password):
    """Generates the authentication header for the API request"""
    b64_string = (base64.b64encode(bytes(
        f"{env_partition}/{uid}:{password}", "utf-8")).decode("ascii")
    )
    auth_header = {"Authorization": f"Basic {b64_string}"}
    return auth_header


def pfx_api_extract(endpoint, header, body=None, label=None):
    """
    Submits the request to the API and retrieves the records in json format.
    Total record count is printed in the terminal.
    Note: Not including a body retreive all data from the endpoint
        - this may not be advisable if it's a large amount of data.
    """
    request_response = requests.post(endpoint, headers=header, json=body)
    raw = json.loads(request_response.text)
    json_response = raw["response"]["data"]
    total_rows = raw["response"]["totalRows"]

    print(f'{label} Total_Rows:{total_rows}')

    return json_response

def transform(json_data, rename=None, col_filter=None):
    """
    Converts the json response to a dataframe,
    optionally renames columns, filters out the unneeded columns
    """
    data = json_data
    data = pd.DataFrame(data)
    # df_renamed = df.rename(columns=rename)
    # df_filter = df_renamed[col_filter]

    return data

def load_to_mssql(data, table_name,connection_string, dtypes=None):
    """
    Inserts a pandad dataframe into a newly created table (if exists replace)
    data types are optional, but can be used if needed.
    """
    print(f'Loading {table_name}.......')
    engine = create_engine(f'{connection_string}',fast_executemany=True)
    data.to_sql(f"{table_name}", schema='dbo', con=engine, if_exists='replace',
                dtype=dtypes)
    print('Load complete')


if __name__ == "__main__":
    # partition = sys.argv[1] #"prod" or "nonprod"\
    TABLE = 'PriceTable' #change this
    parser = configparser.ConfigParser()
    parser.read("pipeline.conf")
    partition = parser.get("pfx credentials","partition_prod")
    pfx_username = parser.get("pfx credentials","username")
    pfx_password = parser.get("pfx credentials","password")
    api_endpoint = parser.get("pfx credentials","pfx_endpoint")
    mssql_username = parser.get("sql server credentials","username")
    mssql_password = parser.get("sql server credentials","password")
    mssql_driver = parser.get("sql server credentials","driver")
    mssql_hostname = parser.get("sql server credentials","hostname_prod")
    mssql_server = parser.get("sql server credentials","server_prod")
    mssql_db_name = parser.get("sql server credentials","database_name")
    mssql_string = (
                    f'mssql+pyodbc://{mssql_username}:{mssql_password}'
                    f'@{mssql_hostname}:1433/{mssql_db_name}?driver={mssql_driver}'
    )
    request_header = b64_auth_header(partition,pfx_username,pfx_password)
    response = pfx_api_extract(api_endpoint,request_header)
    dataframe = transform(response)
    load_to_mssql(dataframe,TABLE,mssql_string)
