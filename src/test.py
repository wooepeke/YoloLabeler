import os
import multiprocessing

def worker():
    print("Worker process running!")

if __name__ == "__main__":
    print(f"Current User: {os.getlogin()}")
    print("Starting multiprocessing...")
    multiprocessing.set_start_method("spawn")
    process = multiprocessing.Process(target=worker)
    process.start()
    process.join()