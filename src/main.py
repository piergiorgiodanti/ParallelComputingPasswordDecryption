import statistics
import threading
from passlib.hash import des_crypt
import random
import string
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import sys
import sysconfig
import itertools
import time
import csv

CHARSET = string.ascii_letters + string.digits + "./"
START_YEAR = 1950
END_YEAR = 2026
N = (END_YEAR - START_YEAR + 1) * 12 * 31

def encrypt_password(password_in_chiaro):
    if len(password_in_chiaro) > 8:
        raise ValueError("La password non può superare gli 8 caratteri!")

    salt = "".join(random.choices(CHARSET, k=2))
    hash_criptato = des_crypt.hash(password_in_chiaro, salt=salt)

    return hash_criptato, salt

def decrypt_passwords(hash_target):
    passwords = generate_date_passwords()
    passwords_trovate = {}
    for password in passwords:
        for (h,s) in hash_target.items():
            if des_crypt.hash(password, salt=s) == h:
                passwords_trovate[h] = password

            if len(passwords_trovate) == len(hash_target):
                return passwords_trovate

    return passwords_trovate

def check_chunk(passwords_chunk, target_hashes, stop_event):
    found_in_chunk = {}
    for password in passwords_chunk:
        if stop_event.is_set():
            return found_in_chunk

        for h_target, s_target in target_hashes.items():
            hash_calcolato = des_crypt.hash(password, salt=s_target)
            if hash_calcolato == h_target:
                found_in_chunk[h_target] = password

    return found_in_chunk

def decrypt_password_par(target_hashes, num_workers, chunk_size):
    iterator = iter(generate_date_passwords())
    stop_event = threading.Event()
    passwords_trovate = {}
    total_targets = len(target_hashes)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = set()

        for _ in range(num_workers * 2):
            chunk = list(itertools.islice(iterator, chunk_size))
            if not chunk: break
            futures.add(executor.submit(check_chunk, chunk, target_hashes, stop_event))

        while futures:  # Fino a quando ci sono task nella coda
            # Si aspetta che almeno uno dei task sia completato
            done, futures = wait(futures, return_when=FIRST_COMPLETED)

            for future in done:
                result = future.result()
                if result:
                    passwords_trovate.update(result)
                    # Se abbiamo trovato tutte le password, segnaliamo lo stop e usciamo
                    if len(passwords_trovate) >= total_targets:
                        stop_event.set()
                        return passwords_trovate

            # Accodiamo nuovi chunk al posto di quelli appena terminati
            if not stop_event.is_set():
                for _ in range(len(done)):
                    chunk = list(itertools.islice(iterator, chunk_size))
                    if chunk:
                        futures.add(executor.submit(check_chunk, chunk, target_hashes, stop_event))

    return passwords_trovate

def generate_date_passwords():
    for year in range(START_YEAR, END_YEAR+1):
        for month in range(1, 13):
            for day in range(1, 32):
                yield f"{day:02d}{month:02d}{year:04d}"

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

def main():

    print_info_GIL()

    passwords = ["01011990", "15082005","31122026"]
    targets = {}
    file_path = "../results/dump/dump_data.csv"
    dump_data = [['Implementazione', 'Threads', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]
    runs = 5

    # Si assume che il salt sia in chiaro
    for password in passwords:
        h, s = encrypt_password(password)
        targets[h] = s

    print("\n\nImplementazione Sequenziale:")

    # Sequenziale
    computation_times = []
    decrypt_passwords(targets) # warm up
    for _ in range(runs):
        time_start = time.perf_counter()
        passwords_trovate = decrypt_passwords(targets)
        time_end = time.perf_counter()
        computation_times.append(time_end - time_start)
        print(f">> {computation_times[_]}")
    median = statistics.median(computation_times)
    dev_standard = statistics.stdev(computation_times)
    print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")
    dump_data.append(['Sequenziale', '-', '-', median, dev_standard])

    print("\n\nImplementazione Parallela:")

    # Parallela
    threads = [2, 4, 6, 8]
    k = 10
    for thread in threads:
        chunk_size = N // (thread * k)
        computation_times = []
        print(f"\nnum. threads: {thread} chunk size: {chunk_size}")
        decrypt_password_par(targets, num_workers=thread, chunk_size=chunk_size) # warm up
        for _ in range(runs):
            time_start = time.perf_counter()
            passwords_trovate = decrypt_password_par(targets, num_workers=thread, chunk_size=chunk_size)
            time_end = time.perf_counter()
            computation_times.append(time_end - time_start)
            print(f">> {computation_times[_]}")
        median = statistics.median(computation_times)
        dev_standard = statistics.stdev(computation_times)
        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")
        dump_data.append(['Parallela', thread, chunk_size, median, dev_standard])

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(dump_data)


    # CHUNK SIZE
    print("\n\nAnalisi Chunk Size:")
    file_path = "../results/dump/dump_data_chunksize.csv"
    dump_data_chunksize = [['Implementazione', 'Threads', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]
    thread = 4
    K = [1, 10, 100, 1000]
    chunks_size = [N // (thread * k) for k in K]
    for chunk_size in chunks_size:
        computation_times = []
        print(f"\nnum. threads: {thread} chunk size: {chunk_size}")
        decrypt_password_par(targets, num_workers=thread, chunk_size=chunk_size)  # warm up
        for _ in range(runs):
            time_start = time.perf_counter()
            passwords_trovate = decrypt_password_par(targets, num_workers=thread, chunk_size=chunk_size)
            time_end = time.perf_counter()
            computation_times.append(time_end - time_start)
            print(f">> {computation_times[_]}")
        median = statistics.median(computation_times)
        dev_standard = statistics.stdev(computation_times)
        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")
        dump_data_chunksize.append(['Parallela', thread, chunk_size, median, dev_standard])

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(dump_data_chunksize)


    # WEAK SCALING
    passwords = ["31122026"]
    targets = {}
    file_path = "../results/dump/dump_data_weakscaling.csv"
    dump_data_weakscaling = [['Implementazione', 'Threads', 'Dataset Size (N)', 'Chunk Size', 'Tempo Medio', 'Deviazione Standard']]

    for password in passwords:
        h, s = encrypt_password(password)
        targets[h] = s

    n_anni_originali = END_YEAR - START_YEAR + 1
    anni_per_thread = max(1, n_anni_originali // 4)

    threads = [1, 2, 4, 6, 8]
    k = 8

    for thread in threads:
        computation_times = []
        anni_correnti = anni_per_thread * thread
        START_YEAR = END_YEAR - anni_correnti
        N = anni_correnti * 12 * 31
        chunk_size = N // (thread * k)

        print(f"Threads: {thread} Data Size: {N} Time: {START_YEAR}-{END_YEAR}")
        decrypt_password_par(targets, num_workers=thread, chunk_size=chunk_size)  # warm up
        for _ in range(runs):
            time_start = time.perf_counter()
            passwords_trovate = decrypt_password_par(targets, num_workers=thread, chunk_size= chunk_size)
            time_end = time.perf_counter()
            computation_times.append(time_end - time_start)
            print(f">> {computation_times[-1]}")
        median = statistics.median(computation_times)
        dev_standard = statistics.stdev(computation_times)
        print(f"Tempo medio: {median} Deviazione standard: {dev_standard}\nPassword trovata: {passwords_trovate}")
        dump_data_weakscaling.append(['Parallela', thread, N, chunk_size, median, dev_standard])

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(dump_data_weakscaling)

if __name__ == "__main__":
    main()