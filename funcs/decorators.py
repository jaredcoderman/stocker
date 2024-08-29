import time

def log_execution_time(func):
    def calculate_time(*args, **kwargs):
        start_time = time.time()

        return_value = func(*args, **kwargs)

        end_time = time.time()
        diff = end_time - start_time
        print(f'FUNCTION: ({func.__name__}) took {diff:.2f} seconds')
        return return_value

    return calculate_time
