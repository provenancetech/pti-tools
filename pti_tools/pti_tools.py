"""
Usage:
    pti_tools.py split_logs <it_log_file> <output_directory>

Commands:
    split_logs:     This command will split a merged IT test log file <it_log_file> that combines the stdout of
                    all services to the <output_directory>. The output directory is erased if present and filled with
                    one log file per service. A problems.log file is also produce to aggregate errors and warnings.

Arguments:
    <it_log_file>:      File containing all the stdouts of all the services when an IT test run was made with the infra local stack
    <output_directory>: Output directory containing the results of the command
"""
from docopt import docopt
from it_log_splitter.splitter import ItLogSplitter


if __name__ == "__main__":
    args = docopt(__doc__)

    if args["split_logs"]:
        splitter = ItLogSplitter()
        splitter.load_log_file(args["<it_log_file>"])
        splitter.split_logs(args["<output_directory>"])
        splitter.write_problem_report(args["<output_directory>"])
