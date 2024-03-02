import os
import pathlib
import time
import psutil
import subprocess
import sys


def load_test_file(file_path):
    with open(file_path, encoding='utf-8') as file:
        return file.read().strip().splitlines()


if __name__ == "__main__":
    module_folder = input("Enter task's folder path from the current root: ")
    tested_file = input("Enter your py-file name to test: ")

    DIR = pathlib.Path(__file__).parent.resolve()
    tests = os.path.join(DIR, f'{module_folder}\\tests')
    executor = os.path.join(DIR, f'executor.py')
    program = load_test_file(os.path.join(DIR, f'{module_folder}\\{tested_file}'))
    print(len(os.listdir(tests)))

    n_tests = len(os.listdir(tests)) // 2
    python_version = 'python3' if sys.platform in {'linux', 'linux2', 'darwin'} else 'python'

    for i in range(1, n_tests + 1):
        process = psutil.Process(os.getpid())
        start_time = time.time()

        test_data = load_test_file(os.path.join(tests, str(i)))
        correct = load_test_file(os.path.join(tests, f'{str(i)}.clue'))

        completed_process = subprocess.run([python_version, executor], input='\n'.join(program + test_data),
                                           capture_output=True, encoding='utf-8')
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

        end_time = time.time()
        elapsed_time = end_time - start_time
        memory_usage = process.memory_info().rss / 1024 / 1024
        print(
            f'Тест №{i} пройден(✓), время выполнения: {elapsed_time:.2f} секунд, использовано памяти: {memory_usage:.2f} MB')
        time.sleep(0.5)
