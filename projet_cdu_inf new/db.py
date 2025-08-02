import oracledb

class OracleDBError(Exception):
    pass

try:
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_8")
except Exception as e:
    print(f"⚠️ Oracle Client Warning: {str(e)}")

def get_connection():
    """Establish Oracle database connection without encoding parameter"""
    try:
        # Basic connection
        conn = oracledb.connect(
            user="CDUGL1Z",
            password="cdugl1z",
            dsn="10.37.22.21:1521/L1ZGE1.world"
        )
        
        # Optional session settings
        with conn.cursor() as cursor:
            cursor.execute("ALTER SESSION SET NLS_LANGUAGE = 'FRENCH'")
            cursor.execute("ALTER SESSION SET NLS_TERRITORY = 'FRANCE'")
        
        return conn
        
    except oracledb.Error as e:
        error, = e.args
        raise OracleDBError(f"Connection Error [{error.code}]: {error.message}")
