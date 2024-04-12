import re
import ssl
import json
import unidecode
import firebase_admin
from google.cloud.firestore_v1 import DocumentSnapshot
from firebase_admin import credentials, firestore
from google_play_scraper import app, search
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context
cred = credentials.Certificate("rayvue-app-firebase-adminsdk-e1e3m-d4c0bef170.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


"""
---------------- TAGS ----------------
1 -> subscription service
2 -> micro-transactions
3 -> battle pass
4 -> loot boxes
5 -> pay to win
6 -> malicious practices
7 -> concerning TOS
8 -> fake engagement
9 -> not as advertised
10 -> immoral developers
11 -> scam
"""


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, DocumentSnapshot):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


# ---------------- 1. ADD A GAME FROM INPUT ----------------
def add_game_from_input():
    game_data = {}
    game_data["id"] = db.collection("games").document().id
    game_data["packageName"] = input("Enter the package name: ")
    game_data["displayName"] = input("Enter the game name: ")
    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )
    game_data["icon"] = input("Enter the icon URL: ")
    game_data["banner"] = input("Enter the banner URL: ")
    game_data["description"] = input("Enter the description: ")
    game_data["price"] = float(input("Enter the price: "))
    game_data["genre"] = float(input("Enter the genre: "))
    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = (
        [int(tag) for tag in tags_input.split(",")] if tags_input else []
    )
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP

    db.collection("games").document(game_data["id"]).set(game_data)
    print("Game added successfully")


# ---------------- 2. ADD A GAME FROM SCRAPER AND INPUT ----------------
def add_game_from_scraper():
    game_data = {}
    game_data["id"] = db.collection("games").document().id
    game_data["packageName"] = input("Enter the package name: ")
    result = app(game_data["packageName"], country="us", lang="en")
    game_data["displayName"] = result["title"]
    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )
    game_data["icon"] = result["icon"]
    if input("Would you like to scrape the banner? (y/n): ").lower() == "y":
        game_data["banner"] = result["headerImage"]
    else:
        game_data["banner"] = input("Enter the banner URL: ")
    game_data["description"] = result["summary"]
    game_data["price"] = float(result["price"])
    game_data["genre"] = result["genre"]
    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = (
        [int(tag) for tag in tags_input.split(",")] if tags_input else []
    )
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP

    db.collection("games").document(game_data["id"]).set(game_data)
    print("Game added successfully")


# ---------------- 3. UPDATE A GAME FROM INPUT ----------------
def update_game_from_input(package_name):
    doc_ref = (
        db.collection("games").where("packageName", "==", package_name).limit(1).get()
    )
    if not doc_ref:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref[0].to_dict()

    print(f"Current data for game with packageName: {package_name}")
    print(json.dumps(game_data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))

    if input("Would you like to update the packageName? (y/n): ").lower() == "y":
        game_data["packageName"] = input("Enter the new packageName: ")

    if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
        game_data["banner"] = input("Enter the new banner URL: ")

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [
            int(tag)
            for tag in input(
                "Enter the new tags (comma-separated, without space): "
            ).split(",")
        ]

    if input("Would you like to update the name? (y/n): ").lower() == "y":
        game_data["displayName"] = input("Enter the new name: ")

    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )

    if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
        game_data["icon"] = input("Enter the new icon URL: ")

    if input("Would you like to update the description? (y/n): ").lower() == "y":
        game_data["description"] = input("Enter the new description: ")

    if input("Would you like to update the price? (y/n): ").lower() == "y":
        game_data["price"] = float(input("Enter the new price: "))

    if input("Would you like to update the genre? (y/n): ").lower() == "y":
        game_data["genre"] = float(input("Enter the new genre: "))

    db.collection("games").document(doc_ref[0].id).update(game_data)
    print("Game updated successfully")


# ---------------- 4. UPDATE A GAME FROM SCRAPER AND INPUT ----------------
def update_game_from_scraper(package_name):
    doc_ref = (
        db.collection("games").where("packageName", "==", package_name).limit(1).get()
    )
    if not doc_ref:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref[0].to_dict()

    print(f"Current data for game with packageName: {package_name}")
    print(json.dumps(game_data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))

    if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
        if game_data["banner"].startswith("https://play-lh.googleusercontent.com"):
            result = app(package_name, country="us", lang="en")
            game_data["banner"] = result["headerImage"]
        else:
            game_data["banner"] = input("Enter the new banner URL: ")

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [
            int(tag)
            for tag in input(
                "Enter the new tags (comma-separated, without space): "
            ).split(",")
        ]

    if input("Would you like to update the packageName? (y/n): ").lower() == "y":
        package_name_input = input("Enter the new packageName: ")
        result = app(package_name_input, country="us", lang="en")
        game_data["packageName"] = package_name_input
        package_name = package_name_input
        game_data["displayName"] = result["title"]
        game_data["displayName"] = (
            game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
        )
        game_data["searchName"] = re.sub(
            r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
        )
        game_data["icon"] = result["icon"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])
        game_data["genre"] = result["genre"]
    else:
        if input("Would you like to update the name? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["displayName"] = result["title"]

        game_data["displayName"] = (
            game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
        )
        game_data["searchName"] = re.sub(
            r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
        )

        if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["icon"] = result["icon"]

        if input("Would you like to update the description? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["description"] = result["summary"]

        if input("Would you like to update the price? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["price"] = float(result["price"])

        if input("Would you like to update the genre? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["genre"] = result["genre"]

    db.collection("games").document(doc_ref[0].id).update(game_data)
    print("Game updated successfully")


# ---------------- 5. UPDATE ALL GAMES FROM SCRAPER ----------------
def update_games_from_scraper():
    docs = db.collection("games").stream()

    for doc in docs:
        game_data = doc.to_dict()
        package_name = game_data["packageName"]

        try:
            result = app(package_name, country="us", lang="en")
        except Exception as e:
            print(f"Skipping game with packageName: {package_name} due to error: {e}")
            continue

        if game_data["banner"].startswith("https://play-lh.googleusercontent.com"):
            game_data["banner"] = result["headerImage"]
        # game_data["displayName"] = result["title"]
        # game_data["displayName"] = (
        #     game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
        # )
        # game_data["searchName"] = re.sub(
        #     r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
        # )
        game_data["icon"] = result["icon"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])
        game_data["genre"] = result["genre"]

        db.collection("games").document(doc.id).update(game_data)
        print(f"Updated game with packageName: {package_name}")

    print("Games updated successfully")


# ---------------- 6. DELETE CERTAIN GAMES ----------------
def delete_games():
    package_names = input(
        "Enter the package names to delete (comma-separated, without space): "
    ).split(",")

    for package_name in package_names:
        package_name = package_name.strip()
        docs = db.collection("games").where("packageName", "==", package_name).stream()

        for doc in docs:
            db.collection("games").document(doc.id).delete()
            print(f"Deleted game with packageName: {package_name}")

    print("Games deleted successfully")


# ---------------- ?. SHOW ALL GAMES ----------------
def list_games():
    docs = db.collection("games").stream()

    for doc in docs:
        game = doc.to_dict()
        print(f"Name: {game['name']}, PackageName: {game['packageName']}")

    print("Games listed successfully")


# ---------------- 7. SEARCH FOR A GAME ----------------
def search_game():
    search_term = input("Enter the search term: ")

    search_results = search(
        search_term,
        lang="en",
        country="us",
        n_hits=3,
    )

    apps_details = []

    for search_result in search_results:
        appId = search_result["appId"]
        app_details = app(appId, lang="en", country="us")

        processed_details = {
            "appId": app_details.get("appId"),
            "icon": app_details.get("icon"),
            "title": app_details.get("title"),
            "genre": app_details.get("genre"),
            "price": app_details.get("price"),
            "developer": app_details.get("developer"),
            "categories": [
                category["name"] for category in app_details.get("categories", [])
            ],
        }

        apps_details.append(processed_details)

    print(f"Search results:")
    print(json.dumps(apps_details, indent=2, ensure_ascii=False))


# ---------------- MAIN ----------------
def main():
    while True:
        print("Options:")
        print("1. Add a game using console")
        print("2. Add a game using scraper")
        print("3. Update a game using console")
        print("4. Update a game using scraper")
        print("5. Update all games using scraper")  # !!! WARNING: COSTLY
        print("6. Delete certain games")
        # print("?. List all games")  # !!! !!! WARNING: SUPER COSTLY
        print("7. Search for a game")
        print("8. Exit")

        option = input("Select an option: ")
        if option == "1":
            add_game_from_input()
        elif option == "2":
            add_game_from_scraper()
        elif option == "3":
            package_name = input("Enter the package name: ")
            update_game_from_input(package_name)
        elif option == "4":
            package_name = input("Enter the package name: ")
            update_game_from_scraper(package_name)
        elif option == "5":
            update_games_from_scraper()
        elif option == "6":
            delete_games()
        # elif option == "?":
        #     list_games()
        elif option == "7":
            search_game()
        elif option == "8":
            break
        else:
            print("Invalid option. Please try again.")

        print()


if __name__ == "__main__":
    main()
