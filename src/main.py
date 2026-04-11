import statistics
import sys
import sysconfig
import time
import csv
import password_decryption as p
import config as c

def is_python_314t():
    v = sys.version_info
    # Python 3.14 and 't' ABI flag (free-threaded build)
    return (v.major, v.minor) == (3, 14) and getattr(sys, "abiflags", "") == "t"

def is_gil_disabled():
    # This config var is defined for free-threaded builds in 3.13+
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

def print_info_GIL():
    print("\nPython version:", sys.version)
    print("ABI flags:", getattr(sys, "abiflags", ""))
    print("is_python_314t:", is_python_314t())
    print("Py_GIL_DISABLED:", sysconfig.get_config_var("Py_GIL_DISABLED"))
    print("is_gil_disabled:", is_gil_disabled())

def build_targets(passwords):
    targets = {}
    for password in passwords:
        h, s = p.encrypt_password(password)
        targets[h] = s
    return targets

def benchmark(func, runs, *args, **kwargs):
    computation_times = []

    func(*args, **kwargs)  # warm up

    for _ in range(runs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        elapsed = end - start
        computation_times.append(elapsed)
        print(f">> {elapsed}")

    median = statistics.median(computation_times) if runs > 1 else 0
    dev_standard = statistics.stdev(computation_times) if runs > 1 else 0

    return median, dev_standard, result


def write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def run_sequential(targets, runs, dump_data):
    print("\n\nImplementazione Sequenziale:")

    median, dev_standard, passwords_trovate = benchmark(
        p.decrypt_passwords, runs, targets
    )

    print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")

    dump_data.append(['Sequenziale', '-', '-', median, dev_standard])


def run_parallel(targets, runs, dump_data, decrypt_password_par, info):
    print(f"\n\n{info}")

    threads = [2, 4, 6, 8]
    k = 10

    for thread in threads:
        chunk_size = c.N // (thread * k)

        print(f"\nnum. threads: {thread} chunk size: {chunk_size}")

        median, dev_standard, passwords_trovate = benchmark(
            decrypt_password_par,
            runs,
            targets,
            num_workers=thread,
            chunk_size=chunk_size
        )

        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")

        dump_data.append([info, thread, chunk_size, median, dev_standard])


def run_chunk_size_analysis(targets, runs, dump_data, decrypt_password_par, info):
    print(f"\n\n{info}")

    thread = 4
    K = [1, 10, 100, 1000]
    chunks_size = [c.N // (thread * k) for k in K]

    for chunk_size in chunks_size:
        print(f"\nnum. threads: {thread} chunk size: {chunk_size}")

        median, dev_standard, passwords_trovate = benchmark(
            decrypt_password_par,
            runs,
            targets,
            num_workers=thread,
            chunk_size=chunk_size
        )

        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")

        dump_data.append([info, thread, chunk_size, median, dev_standard])

def run_weak_scaling(targets, runs, dump_data, decrypt_password_par, info):
    print(f"\n\n{info}")
    c.START_YEAR = 1950
    n_anni_originali = c.END_YEAR - c.START_YEAR + 1
    anni_per_thread = max(1, n_anni_originali // 4)

    threads = [1, 2, 4, 6, 8]
    k = 8

    for thread in threads:

        anni_correnti = anni_per_thread * thread
        c.START_YEAR = c.END_YEAR - anni_correnti
        c.N = anni_correnti * 12 * 31
        chunk_size = c.N // (thread * k)

        print(f"Threads: {thread} Data Size: {c.N} Time: {c.START_YEAR}-{c.END_YEAR}")

        median, dev_standard, passwords_trovate = benchmark(
            decrypt_password_par,
            runs,
            targets,
            num_workers=thread,
            chunk_size=chunk_size
        )

        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")

        dump_data.append([info, thread, c.N, chunk_size, median, dev_standard])

def run_benchmarks():

    print_info_GIL()

    runs = 5

    passwords = ["01011990", "15082005", "31122026"]
    targets = build_targets(passwords)

    print(f"\nLista di password: {passwords} da trovare.")

    file_path = "../results/dump/dump_data.csv"
    dump_data = [['Implementazione', 'Threads', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]

    run_sequential(targets, runs, dump_data)
    run_parallel(targets, runs, dump_data, p.decrypt_password_par_pool, "Parallel Pool")
    run_parallel(targets, runs, dump_data, p.decrypt_password_par_threads, "Parallel Threads")

    write_csv(file_path, dump_data)

    file_path = "../results/dump/dump_data_chunksize.csv"
    dump_data = [['Implementazione', 'Threads', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]

    run_chunk_size_analysis(targets, runs, dump_data, p.decrypt_password_par_pool, "Parallel Pool")
    run_chunk_size_analysis(targets, runs, dump_data, p.decrypt_password_par_threads, "Parallel Threads")

    write_csv(file_path, dump_data)

    passwords = ["31122026"]
    targets = build_targets(passwords)

    file_path = "../results/dump/dump_data_weakscaling.csv"
    dump_data = [['Implementazione', 'Threads', 'Dataset Size (N)', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]

    run_weak_scaling(targets, runs, dump_data, p.decrypt_password_par_pool, "Parallel Pool")
    run_weak_scaling(targets, runs, dump_data, p.decrypt_password_par_threads, "Parallel Threads")

    write_csv(file_path, dump_data)

def run_demo():
    print_info_GIL()
    passwords = ["01011990", "f5082005", "31122026"]
    targets = build_targets(passwords)
    threads = 4
    chunk_size = c.N // (threads * 10)

    print(f"\nLista di password: {passwords} da trovare.")

    print("\nSequenziale:")

    start = time.perf_counter()
    passwords_trovate = p.decrypt_passwords(targets)
    end = time.perf_counter()

    print(f"Passwords trovate: {passwords_trovate}")
    print("Tempo di esecuzione: ", end - start)

    print("\nParallela con pool di thread:")

    start = time.perf_counter()
    passwords_trovate = p.decrypt_password_par_pool(targets, threads, chunk_size)
    end = time.perf_counter()

    print(f"Passwords trovate: {passwords_trovate}")
    print("Tempo di esecuzione: ", end - start)

    print("\nParallela con thread:")

    start = time.perf_counter()
    passwords_trovate = p.decrypt_password_par_threads(targets, threads, chunk_size)
    end = time.perf_counter()

    print(f"Passwords trovate: {passwords_trovate}")
    print("Tempo di esecuzione: ", end - start)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Parametro obbligatorio, scegliere tra 'benchmark' e 'demo'")
    else:
        if sys.argv[1] == "benchmark": run_benchmarks()
        else:
            if sys.argv[1] == "demo":  run_demo()
            else: print("Parametro obbligatorio, scegliere tra 'benchmark' e 'demo'")
