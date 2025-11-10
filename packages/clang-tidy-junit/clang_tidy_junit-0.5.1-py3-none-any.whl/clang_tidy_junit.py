"""Convert Clang-Tidy output to JUnit XML"""

import itertools
import re
import sys
from junitparser import Error, JUnitXml, TestCase, TestSuite
from junitparser.junitparser import FinalResult

error_regex = re.compile(r"(.+)(:\d+:\d+: \w+:.+) (\[.+\])")
warn_regex = re.compile(r"\d+ warnings? generated\.")


def process_error(error: list[str]) -> tuple[str, Error]:
    """process an error line"""
    m = error_regex.fullmatch(error[0].strip())
    assert m
    jerror = Error(m.group(1) + m.group(2), m.group(3))
    jerror.text = "".join(error)
    return (m.group(1), jerror)


def parse_log(logfile: str) -> list[tuple[str, Error]]:
    """parse clang-tidy log to a list of errors"""
    errors: list[tuple[str, Error]] = []
    buffer: list[str] = []
    with open(logfile, "r", encoding="utf-8") as f:
        for line in f:
            if error_regex.fullmatch(line.strip()):
                if buffer:
                    errors.append(process_error(buffer))
                buffer = [line]
            elif buffer and not warn_regex.fullmatch(line.strip()):
                buffer.append(line)

    if buffer:
        errors.append(process_error(buffer))
    return errors


def generate_test_case(name: str, errors: list[tuple[str, Error]]) -> TestCase:
    """generate a test case"""
    test_case = TestCase(name)
    jerrors: list[FinalResult] = []
    for e in errors:
        jerrors.append(e[1])
    test_case.result = jerrors
    return test_case


def generate_test_suite(errors: list[tuple[str, Error]]) -> TestSuite:
    """generate a test suite"""
    test_suite = TestSuite("Clang-Tidy")  # type: ignore
    if errors:
        errors = sorted(errors, key=lambda e: e[0])
        for file, it in itertools.groupby(errors, key=lambda e: e[0]):
            test = generate_test_case(file, list(it))
            test_suite.add_testcase(test)
    else:
        test = generate_test_case("Clang-Tidy", [])
        test_suite.add_testcase(test)
    return test_suite


def process(logfile: str, junitfile: str) -> int:
    """convert clang-tidy log to junit"""
    errors = parse_log(logfile)
    tree = JUnitXml("Clang-Tidy")  # type: ignore
    tree.add_testsuite(generate_test_suite(errors))
    tree.write(junitfile)
    return 0


def main() -> int:  # pragma: no cover
    """main function"""
    if len(sys.argv) != 3:
        print("usage: clang-tidy-junit input.log output.xml")
        return 1
    return process(sys.argv[1], sys.argv[2])


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
