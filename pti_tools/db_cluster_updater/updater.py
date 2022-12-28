from typing import List

from psycopg2 import connect


class ClusterUpdater():

    def __init__(self, cluster_url: str, username: str, password: str, databases: List[str]):
        self.cluster_url = cluster_url
        self.username = username
        self.password = password
        self.databases = databases

    def update_databases(self, query: str):

        for database in self.databases:
            print(f"Connecting to {self.cluster_url}/{database} with user {self.username}")
            con = connect(host=self.cluster_url, dbname=database, user=self.username, password=self.password)
            cur = con.cursor()
            print(f"Executing the following query on {database}: {query}")
            cur.execute(query)
            con.commit()
            cur.close()
            con.close()
