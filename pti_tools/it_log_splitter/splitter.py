import shutil
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel as PydanticBase

class ServiceCounts(PydanticBase):
    error_count: int
    warning_count: int

class ServiceProblems(PydanticBase):
    errors: List[str] = []
    warnings: List[str] = []

class ItLogSplitter:

    original_lines: List[str]
    start_idx: int = 0
    service_problems: Dict[str, ServiceProblems] = dict()
    splitted_lines: Dict[str, List[str]] = dict()

    def load_log_file(self, filename: str):

        with open(filename) as f:
            self.original_lines = f.readlines()

        # figure out start of logs
        for idx, line in enumerate(self.original_lines):
            if "##[endgroup]" not in line:
                continue
            else:
                self.start_idx = idx + 1
                break

    @property
    def log_lines(self) -> List[str]:
        return self.original_lines[self.start_idx:]

    def split_logs(self, output_directory: str):
        shutil.rmtree(output_directory, ignore_errors=True)
        Path(output_directory).mkdir(parents=True, exist_ok=False)

        for idx, line in enumerate(self.log_lines):
            parts = line.split()
            service = parts[1]

            start = line.find("|")
            cleaned_line = line[start+2:]
            if service in self.splitted_lines:
                self.splitted_lines[service].append(cleaned_line)
            else:
                self.splitted_lines[service] = [cleaned_line]

            if len(parts) > 5:
                log_level = parts[5]
                self.accumulate_problems(service, log_level, cleaned_line)

        for service, lines in self.splitted_lines.items():
            output_filepath = Path(output_directory) / f"{service}.log"

            with open(output_filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)

    def accumulate_problems(self, service, log_level, line):
        if log_level not in ["INFO", "WARNING", "ERROR", "DEBUG", "TRACE"]:
            log_level = None

        if log_level and log_level in ["WARNING", "ERROR"]:
            problem_line_idx = len(self.splitted_lines[service]) + 1
            problem_line = f"{problem_line_idx:4}: {line}"
            if service in self.service_problems:
                if log_level == "ERROR":
                    self.service_problems[service].errors.append(problem_line)
                else:
                    self.service_problems[service].warnings.append(problem_line)
            else:
                if log_level == "ERROR":
                    self.service_problems[service] = ServiceProblems(errors=[problem_line])
                else:
                    self.service_problems[service] = ServiceProblems(warnings=[problem_line])

    def write_problem_report(self, output_directory):

        report_lines: List[str] = []

        for service, problems in self.service_problems.items():
            if problems.errors:
                report_lines.append(f"\n{service} ERRORS\n")
                report_lines.extend(problems.errors)

        report_lines.append("\n\n")

        for service, problems in self.service_problems.items():
            if problems.warnings:
                report_lines.append(f"\n{service} WARNINGS\n")
                report_lines.extend(problems.warnings)

        summary_lines = self.create_problem_summary()
        print("".join(summary_lines))

        output_filepath = Path(output_directory) / f"problems.log"

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("Problems summary:\n")
            f.writelines(summary_lines)
            f.write("\nProblems details:\n")
            f.writelines(report_lines)

    def create_problem_summary(self) -> List[str]:
        summary_lines: List[str] = []

        total_errors = sum(len(problems.errors) for problems in self.service_problems.values())
        total_warnings = sum(len(problems.warnings) for problems in self.service_problems.values())

        summary_lines.append(f"{total_errors} errors and {total_warnings} warnings detected\n")

        for service, problems in self.service_problems.items():
            summary_lines.append(f"{service:40}: {len(problems.errors):3} errors, {len(problems.warnings):3} warnings\n")

        return summary_lines




if __name__ == "__main__":
    splitter = ItLogSplitter()

    splitter.load_log_file("services.txt")

    splitter.split_logs("split")

    splitter.write_problem_report("split")
