"""
Usage:
    pti_tools.py split_logs <it_log_file> <output_directory>
    pti_tools.py unlock_dbs <cluster_url> <cluster_password>

Commands:
    split_logs:     This command will split a merged IT test log file <it_log_file> that combines the stdout of
                    all services to the <output_directory>. The output directory is erased if present and filled with
                    one log file per service. A problems.log file is also produce to aggregate errors and warnings.

    unlock_dbs:     This command will send `UPDATE DATABASECHANGELOGLOCK SET LOCKED=false` to all databases managed
                    by liquibase ( list maintained in db_cluster_updater/db_list.py ) in the specified cluster

Arguments:
    <it_log_file>:      File containing all the stdouts of all the services when an IT test run was made with the infra local stack
    <output_directory>: Output directory containing the results of the command
    <cluster_url>     : Url of the write instance in the db cluster
    <cluster_password>: Root password for all dbs in cluster ( defaults to "pti" user )
"""
from docopt import docopt
from it_log_splitter.splitter import ItLogSplitter
from db_cluster_updater.updater import ClusterUpdater
from db_cluster_updater.db_list import LIQUIBASE_DB_LIST

if __name__ == "__main__":
    args = docopt(__doc__)

    if args["split_logs"]:
        splitter = ItLogSplitter()
        splitter.load_log_file(args["<it_log_file>"])
        splitter.split_logs(args["<output_directory>"])
        splitter.write_problem_report(args["<output_directory>"])
    elif args["unlock_dbs"]:
        updater = ClusterUpdater(cluster_url=args["<cluster_url>"], username="pti", password=args["<cluster_password>"], databases=LIQUIBASE_DB_LIST)
        query = "UPDATE DATABASECHANGELOGLOCK SET LOCKED=false"
        updater.update_databases(query=query)
