# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

import requests
import string
import random

URL_SOURCE = (
    "https://pristy.ged/alfresco/api/-default-/public/alfresco/versions/1/people"
)
URL_TARGET = (
    "https://pristy.demo/alfresco/api/-default-/public/alfresco/versions/1/people"
)

HEADERS_SOURCE = {
    "Authorization": "Basic XXXXXXXXXXXXX",
    "Content-Type": "application/json",
}
HEADERS_TARGET = {
    "Authorization": "Basic XXXXXXXXXXX",
    "Content-Type": "application/json",
}

MAX_ITEMS_PER_PAGE = 10


def fetch_users(skip_count):
    params = {"skipCount": skip_count, "maxItems": MAX_ITEMS_PER_PAGE}
    try:
        print("Ask for users")
        response = requests.get(
            URL_SOURCE, headers=HEADERS_SOURCE, params=params, verify=False
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des utilisateurs: {e}")
        return []


def generate_random_password(length=24):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(characters) for _ in range(length))


def process_user(user_entry):
    user = user_entry.get("entry", {})
    user["password"] = generate_random_password()
    print(f"Injection de l'utilisateur {user.get('id')}")
    print(user)
    try:
        response = requests.post(URL_TARGET, json=user, headers=HEADERS_TARGET)
        response.raise_for_status()
        print(f"Utilisateur {user.get('id')} traité avec succès.")
    except requests.RequestException as e:
        print(f"Erreur lors du traitement de l’utilisateur {user.get('id')}: {e}")


def main():
    skip_count = 0
    while True:
        data = fetch_users(skip_count)
        if not data:
            break  # Erreur ou fin de pagination

        entries = data.get("list", {}).get("entries", [])
        for user_entry in entries:
            # TODO filter les comptes internes uniquement
            process_user(user_entry)

        pagination = data.get("list", {}).get("pagination", {})
        has_more = pagination.get("hasMoreItems", False)

        if not has_more:
            break

        skip_count += MAX_ITEMS_PER_PAGE


if __name__ == "__main__":
    main()
