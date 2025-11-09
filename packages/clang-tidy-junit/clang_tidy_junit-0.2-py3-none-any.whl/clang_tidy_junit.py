"""Convert Clang-Tidy output to JUnit XML"""

import itertools
import re
import sys
from junitparser import Error, JUnitXml, TestCase, TestSuite
from junitparser.junitparser import FinalResult

error_regex = re.compile(r"^([\w\/\.\+\-\ ]+)(:\d+:\d+: .+) (\[[\w\-,\.]+\])$")
warn_regex = re.compile(r"^[0-9]+ warning[s]? generated\.$")


def process_error(error: list[str]) -> tuple[str, Error]:
    """process an error line"""
    result = error_regex.match(error[0])
    assert result
    jerror = Error(result.group(1) + result.group(2), result.group(3))
    jerror.text = "".join(error)
    return (result.group(1), jerror)


def parse_log() -> list[tuple[str, Error]]:
    """parse clang-tidy log to a list of errors"""
    errors: list[tuple[str, Error]] = []
    buffer: list[str] = []
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        for line in f:
            if error_regex.match(line):
                if buffer:
                    errors.append(process_error(buffer))
                buffer = [line]
            elif buffer and not warn_regex.match(line):
                buffer.append(line)

    if buffer:
        errors.append(process_error(buffer))
    return errors


def generate_test_case(
    name: str, class_name: str, errors: list[tuple[str, Error]]
) -> TestCase:
    """generate a test case"""
    test_case = TestCase(name, class_name, 1)
    jerrors: list[FinalResult] = []
    for e in errors:
        jerrors.append(e[1])
    test_case.result = jerrors
    return test_case


def generate_test_suite(errors: list[tuple[str, Error]]) -> TestSuite:
    """generate a test suite"""
    test_suite = TestSuite("Clang-Tidy")
    if errors:
        errors = sorted(errors, key=lambda e: e[0])
        for file, it in itertools.groupby(errors, key=lambda e: e[0]):
            test = generate_test_case(file, "Clang-Tidy error", list(it))
            test_suite.add_testcase(test)
    else:
        test = generate_test_case("Clang-Tidy", "Clang-Tidy success", [])
        test_suite.add_testcase(test)
    return test_suite


def main() -> int:
    """main function"""
    if len(sys.argv) != 3:
        print("usage: clang-tidy-junit input.log output.xml")
        return 0
    errors = parse_log()
    tree = JUnitXml("Clang-Tidy")
    tree.add_testsuite(generate_test_suite(errors))
    tree.write(sys.argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
