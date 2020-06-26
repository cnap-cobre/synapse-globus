import psycopg2
import json
from sshtunnel import SSHTunnelForwarder
from sshtunnel import open_tunnel


class DB:
    svr: str = 'localhost'
    dbname: str = 'dvndb'
    usr: str = ''
    passcode: str = ''
    use_ssh: bool = False
    ssh_host: str = ''
    ssh_port: int = -1
    ssh_usr: str = ''
    ssh_pass: str = ''
    credentials_path: str = ''

    def __init__(self, credential_path: str):
        self.credentials_path = credential_path

        with open(credential_path, 'r') as f:
            raw: str = f.read()
        d = json.loads(raw)
        self.svr = d['DB_HOST']
        self.db_port = d['DB_PORT']
        self.dbname = d['DB_NAME']
        self.usr = d['DB_USR']
        self.passcode = d['DB_PASS']
        self.use_ssh = d['DB_USE_SSH']
        self.ssh_host = d['SSH_HOST']
        self.ssh_port = d['SSH_PORT']
        self.ssh_usr = d['SSH_USER']
        self.ssh_pass = d['SSH_PASS']

    def execute(self, method, **kwargs):
        try:
            conn = None
            result = None
            if self.use_ssh:
                with open_tunnel((self.ssh_host, self.ssh_port),
                                 ssh_username=self.ssh_usr,
                                 ssh_password=self.ssh_pass,
                                 remote_bind_address=(
                        self.svr, self.db_port),
                        local_bind_address=(self.svr, self.db_port)) as sshserver:
                    conn = psycopg2.connect(
                        host=self.svr, database=self.dbname, user=self.usr, password=self.passcode)
                    result = method(conn, **kwargs)
                    sshserver.stop()
                return result
            else:
                conn = psycopg2.connect(
                    host=self.svr, database=self.dbname, user=self.usr, password=self.passcode, port=self.db_port)
                return method(conn)
        except (Exception, psycopg.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def get_dv_api_keys(self, conn, **kwargs):
        result = []
        cur = conn.cursor()
        cur.execute("SELECT tokenstring FROM apitoken")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            result.append(row[0])
        cur.close()
        return result

    def get_bytes_of_dataset(self, conn, **kwargs):
        cur = conn.cursor()

        qry: str = """ select sum(filesize) as sum_size
                      from(
                        select filesize
                        from datafile
                        join dvobject on dvobject.id = datafile.id
                        join dataset on dataset.id = dvobject.owner_id
                        where dataset.id = %s
                      ) as sumsubquery;"""

        cur.execute(qry, [kwargs['dataset_id']])
        rows = cur.fetchall()
        return rows[0][0]

    def get_downloads_of_dataset(self, conn, **kwargs):
        cur = conn.cursor()

        qry: str = """ select *
                        from guestbookresponse order by responsetime;"""

        cur.execute(qry, [kwargs['dataset_id']])
        rows = cur.fetchall()
        return row[0]
