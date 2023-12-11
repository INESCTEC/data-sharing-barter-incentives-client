import itertools

first_names = ["Alex", "Bob", "Cleo", "Dina", "Eve"]
last_names = ["Smith", "Doe", "Wong", "Park", "Chen"]


def generate_users(nr_users: int):
    # Generate all unique combinations of first_names and last_names
    names = list(itertools.product(first_names, last_names))
    # Shuffle the list to make it random
    if nr_users > len(names):
        raise Exception(
            "Too many users requested."f" Can't generate more than {len(names)} unique name combinations.")

    passwords = ["ola123456!" for _ in range(nr_users)]
    agent_info_list = []
    for name, password in zip(names, passwords):
        first_name = str(name[0])
        last_name = name[1]
        agent_info_list.append({
            "email": f"{first_name.lower()}.{last_name.lower()}@inesctec.pt",
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "role": [1, 2]  # buyer & seller
        })

    return agent_info_list
