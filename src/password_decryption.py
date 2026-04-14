import threading
from passlib.hash import des_crypt
import random
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, as_completed
import itertools
import config

def encrypt_password(password_in_chiaro):
    if len(password_in_chiaro) > 8:
        raise ValueError("La password non può superare gli 8 caratteri.")

    salt = "".join(random.choices(config.CHARSET, k=2))
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

def decrypt_password_par_pool(target_hashes, num_workers, chunk_size):
    iterator = iter(generate_date_passwords())
    stop_event = threading.Event()
    passwords_trovate = {}
    total_targets = len(target_hashes)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = set()

        # Si riempiono il pool con i primi task
        for _ in range(num_workers):
            chunk = list(itertools.islice(iterator, chunk_size))
            if not chunk:
                break
            futures.add(executor.submit(check_chunk, chunk, target_hashes, stop_event))

        while futures and not stop_event.is_set():
            # Si aspetta che almeno task finisca
            done, not_done = wait(futures, return_when=FIRST_COMPLETED)

            # Si analizza i task completati
            for future in done:
                result = future.result()
                if result:
                    passwords_trovate.update(result)
                    # Se trovato tutti i task si termina la ricerca
                    if len(passwords_trovate) >= total_targets:
                        stop_event.set()
                        return passwords_trovate

            # futures correnti con solo quelli non ancora finiti
            futures = not_done

            # Se non abbiamo finito di cercare, si rimpiazzano i task appena terminati
            if not stop_event.is_set():
                for _ in range(len(done)):
                    chunk = list(itertools.islice(iterator, chunk_size))
                    if chunk:  # si abilita un nuovo task solo se c'è ancora qualcosa nell'iteratore
                        futures.add(executor.submit(check_chunk, chunk, target_hashes, stop_event))
                    else:
                        break
    return passwords_trovate

def generate_date_passwords():
    for year in range(config.START_YEAR, config.END_YEAR+1):
        for month in range(1, 13):
            for day in range(1, 32):
                yield f"{day:02d}{month:02d}{year:04d}"
