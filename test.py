import os
import pathlib
import time
import psutil
import subprocess
import sys
import re


def load_test_file(file_path):
    with open(file_path, encoding='utf-8') as file:
        return file.read().strip().splitlines()


if __name__ == "__main__":
    module_folder, tested_file = input("Enter task's folder path from the current root and py-file name: ").split()

    DIR = pathlib.Path(__file__).parent.resolve()
    tests = os.path.join(DIR, f'{module_folder}\\tests')
    executor = os.path.join(DIR, f'executor.py')
    program = load_test_file(os.path.join(DIR, f'{module_folder}\\{tested_file}'))

    n_tests = len(os.listdir(tests)) // 2
    python_version = 'python3' if sys.platform in {'linux', 'linux2', 'darwin'} else 'python'

    for i in range(1, n_tests + 1):
        process = psutil.Process(os.getpid())
        start_time = time.time()

        correct = load_test_file(os.path.join(tests, f'{str(i)}.clue'))
        test_data = load_test_file(os.path.join(tests, str(i)))

        check_if_function = any(
            map(lambda line: re.search(r"print(.*?)", line), test_data))

        try:
            if check_if_function:
                completed_process = subprocess.run([python_version, executor],
                                                   input='\n'.join(
                                                       program + test_data),
                                                   capture_output=True,
                                                   encoding='utf-8',
                                                   check=True)
            else:
                executor_file = os.path.join(DIR,
                                             f'{module_folder}\\{tested_file}')
                completed_process = subprocess.run(
                    [python_version, executor_file],
                    input='\n'.join(test_data),
                    capture_output=True,
                    encoding='utf-8',
                    check=True)
            result_bytes = completed_process.stdout
            result = result_bytes.strip().splitlines()

            if result != correct:
                print(f"Test#{i} Input:")
                print('\n'.join(test_data))
                print(f"Test#{i} Expected Output:")
                print('\n'.join(correct))
                print(f"Test#{i} Actual Output:")
                print('\n'.join(result))

            assert result == correct, f"Test#{i}\n{'-' * 69}\nexpect:{repr(correct)}\nresult:{repr(result)}\n"

        except subprocess.CalledProcessError as e:
            print(f"\n 💀 💀 💀 Тест №{i} провален:{e}")
            print(f"\n\tError message: {e.stderr}\n")
            break
        except Exception as e:
            print(f"Test#{i} failed with an unexpected error: {e}")
            print(f"Error type: {type(e).__name__}")
            break

        end_time = time.time()
        elapsed_time = end_time - start_time
        memory_usage = process.memory_info().rss / 1024 / 1024
        print(
            f'Тест №{i} пройден(✓), время выполнения: {elapsed_time:.2f} секунд, использовано памяти: {memory_usage:.2f} MB')
