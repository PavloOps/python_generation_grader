import ast
import os
import pathlib
import re
import subprocess
import sys
import time
import traceback
from typing import List

import chardet
import psutil


def prints_something(file_content: str) -> bool:
    tree = ast.parse(file_content)
    return any(
        isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print"
        for node in ast.walk(tree)
    )


def contains_function_def(file_content: str) -> bool:
    tree = ast.parse(file_content)
    return any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))


def find_all_solution_files(directory: str, pattern=r"task\d+\.py") -> list[str]:
    scripts = []

    for root, _, files in os.walk(directory):
        for file_name in files:
            if bool(re.search(pattern, file_name)):
                scripts.append(os.path.join(root, file_name))
    return scripts


def load_test_file(file_path: str, return_encoding=False) -> list | tuple:
    with open(file_path, encoding="utf-8") as file, open(
        file_path, "rb"
    ) as binary_file:
        raw_data = binary_file.read()
        file_encoding = chardet.detect(raw_data)["encoding"]
        file_content = file.read().strip().splitlines()

        if return_encoding:
            return file_content, file_encoding
        return file_content


def run_test(
    file: str,
    test_index: int,
    executor_file: str,
    input_data: str | bytes,
    correct: List[str],
    encoding: str,
    python_version: str,
    test_data: List[str],
) -> bool:

    try:
        completed_process = subprocess.run(
            [python_version, executor_file],
            input=input_data,
            capture_output=True,
            encoding=None if contains_function_def(input_data) else encoding,
            check=True,
        )

        output = completed_process.stdout
        result = (
            output.decode().strip().splitlines()
            if isinstance(output, bytes)
            else output.splitlines()
        )

        if result != correct:
            print(f"Test#{test_index} Input:" + "\n".join(test_data))
            print(f"Test#{test_index} Expected Output:" + "\n".join(correct))
            print(f"Test#{test_index} Actual Output:" + "\n".join(result))

        assert (
            result == correct
        ), f"Test#{test_index}\n{'-' * 69}\nexpect:{repr(correct)}\nresult:{repr(result)}\n"

    except subprocess.CalledProcessError as e:
        print(f"\n 💀 💀 💀 Тест №{test_index} провален: {e}")
        print(f"\n\tError message: {e.stderr}\n")
        log_error(file)
        return False

    except Exception as e:
        print(f"\n 😱 😱 😱 Test#{test_index} failed with an unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        log_error(file)
        return False

    return True


def log_error(file: str) -> None:
    with open(
        "./errors.txt", "a"
    ) as errors_file:
        print(file, file=errors_file)


if __name__ == "__main__":
    script_file = input(
        "Enter task's folder path from the current root and py-file name: "
    )
    module_folder, tested_file = os.path.split(script_file)
    DIR = pathlib.Path(__file__).parent.resolve()
    tests_dir = os.path.join(DIR, f"{module_folder}/tests")
    executor = os.path.join(DIR, "executor.py")
    program_path = os.path.join(DIR, script_file)
    program = load_test_file(program_path)
    solution_syntax = "\n".join(program)

    n_tests = len(os.listdir(tests_dir)) // 2
    python_version = (
        "python3" if sys.platform in {"linux", "linux2", "darwin"} else "python"
    )

    for i in range(1, n_tests + 1):
        process = psutil.Process(os.getpid())
        start_time = time.time()
        test_file_path = os.path.join(tests_dir, f"{i}.clue")

        correct, encoding = load_test_file(test_file_path, return_encoding=True)
        test_data = load_test_file(os.path.join(tests_dir, str(i)))

        input_data = (
            "\n".join(program + test_data).encode()
            if contains_function_def(solution_syntax)
            else "\n".join(test_data)
        )

        executor_file = (
            executor
            if contains_function_def(solution_syntax)
            and prints_something(solution_syntax)
            else (
                os.path.join(DIR, script_file)
                if not contains_function_def(solution_syntax)
                else executor
            )
        )

        if not run_test(
            file=script_file,
            test_index=i,
            executor_file=executor_file,
            input_data=input_data,
            correct=correct,
            encoding=encoding,
            python_version=python_version,
            test_data=test_data,
        ):
            break

        end_time = time.time()
        elapsed_time = end_time - start_time
        memory_usage = process.memory_info().rss / 1024 / 1024
        print(
            f"Тест №{i} пройден (✓), время: {elapsed_time:.2f} секунд, память: {memory_usage:.2f} MB"
        )
