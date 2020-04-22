import psycopg2


class DB:
    svr: str = 'localhost'
    dbname: str = 'dvndb'
    usr: str = ''
    passcode: str = ''

    def __init__(self, usr: str, passcode: str, svr: str = 'localhost', database_name: str = 'dvndb'):
        self.svr = svr
        self.dbname = database_name
        self.usr = usr
        self.passcode = passcode

    def get_dv_api_keys(self):
        result = []
        try:
            conn = psycopg2.connect(
                host=svr, database=dbname, user=usr, password=passcode)
            cur = conn.cursor()
            cur.execute("SELECT tokenstring FROM apitoken")
            rows = cur.fetchall()
            for row in rows:
                print(row)
                result.append(row)
            cur.close()
        except (Exception, psycopg.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
