def palindromes():
    num = 1
    while True:
        num_str = str(num)
        if num_str == num_str[::-1]:
            yield num
        num += 1
