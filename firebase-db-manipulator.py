import os
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


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, DocumentSnapshot):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


# ---------------- 1. ADD A GAME FROM INPUT ----------------
def add_game_from_input(package_name):
    # insert data
    game_data = {}
    game_data["id"] = package_name
    game_data["displayName"] = input("Enter the game name: ")
    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )
    game_data["developer"] = input("Enter the developer: ")
    game_data["icon"] = input("Enter the icon URL: ")
    game_data["banner"] = input("Enter the banner URL: ")
    game_data["description"] = input("Enter the description: ")
    game_data["price"] = float(input("Enter the price: "))
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP
    game_data["genre"] = float(input("Enter the genre: "))

    categories_input = input("Enter the categories (comma-separated, without space): ")
    game_data["categories"] = (
        [category.strip() for category in categories_input.split(",")]
        if categories_input
        else []
    )

    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = (
        [int(tag) for tag in tags_input.split(",")] if tags_input else []
    )

    # send data to Firebase
    if game_data["genre"].lower() == "role playing":
        genre_doc_name = "rolePlaying"
    else:
        genre_doc_name = game_data["genre"].lower()

    db.collection("gameIds").document(genre_doc_name).update(
        {"idsList": firestore.ArrayUnion([package_name])}
    )
    db.collection("gameIds").document("all").update(
        {"idsList": firestore.ArrayUnion([package_name])}
    )
    db.collection("games").document(package_name).set(game_data)
    print("Game added successfully")


# ---------------- 2. ADD A GAME FROM SCRAPER AND INPUT ----------------
def add_game_from_scraper(package_name):
    # insert data
    result = app(package_name, country="us", lang="en")

    game_data = {}
    game_data["id"] = package_name
    game_data["displayName"] = result["title"]
    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )
    game_data["developer"] = result["developer"]
    game_data["icon"] = result["icon"]

    if input("Would you like to scrape the banner? (y/n): ").lower() == "y":
        game_data["banner"] = result["headerImage"]
    else:
        game_data["banner"] = input("Enter the banner URL: ")

    game_data["description"] = result["summary"]
    game_data["price"] = float(result["price"])
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP
    game_data["genre"] = result["genre"]
    game_data["categories"] = [category["name"] for category in result["categories"]]

    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = (
        [int(tag) for tag in tags_input.split(",")] if tags_input else []
    )

    # send data to Firebase
    if game_data["genre"].lower() == "role playing":
        genre_doc_name = "rolePlaying"
    else:
        genre_doc_name = game_data["genre"].lower()

    db.collection("gameIds").document(genre_doc_name).update(
        {"idsList": firestore.ArrayUnion([package_name])}
    )
    db.collection("gameIds").document("all").update(
        {"idsList": firestore.ArrayUnion([package_name])}
    )
    db.collection("games").document(package_name).set(game_data)
    print("Game added successfully")


# ---------------- 3. UPDATE A GAME FROM INPUT ----------------
def update_game_from_input(package_name):
    doc_ref = db.collection("games").document(package_name).get()

    if not doc_ref.exists:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref.to_dict()

    print(f"Current data for game with packageName: {package_name}")
    print(json.dumps(game_data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))

    if input("Would you like to update the name? (y/n): ").lower() == "y":
        game_data["displayName"] = input("Enter the new name: ")

    game_data["displayName"] = (
        game_data["displayName"].replace("™", "").replace("©", "").replace("®", "")
    )
    game_data["searchName"] = re.sub(
        r"[^a-z0-9]", "", unidecode.unidecode(game_data["displayName"].lower())
    )

    if input("Would you like to update the developer? (y/n): ").lower() == "y":
        game_data["developer"] = input("Enter the new developer: ")

    if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
        game_data["icon"] = input("Enter the new icon URL: ")

    if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
        game_data["banner"] = input("Enter the new banner URL: ")

    if input("Would you like to update the description? (y/n): ").lower() == "y":
        game_data["description"] = input("Enter the new description: ")

    if input("Would you like to update the price? (y/n): ").lower() == "y":
        game_data["price"] = float(input("Enter the new price: "))

    if input("Would you like to update the genre? (y/n): ").lower() == "y":
        game_data["genre"] = float(input("Enter the new genre: "))

    if input("Would you like to update the categories? (y/n): ").lower() == "y":
        game_data["categories"] = [
            category.strip()
            for category in input(
                "Enter the new categories (comma-separated, without space): "
            ).split(",")
        ]

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [
            int(tag)
            for tag in input(
                "Enter the new tags (comma-separated, without space): "
            ).split(",")
        ]

    db.collection("games").document(package_name).update(game_data)
    print("Game updated successfully")


# ---------------- 4. UPDATE A GAME FROM SCRAPER AND INPUT ----------------
def update_game_from_scraper(package_name):
    doc_ref = db.collection("games").document(package_name).get()

    if not doc_ref.exists:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref.to_dict()
    result = app(package_name, country="us", lang="en")

    print(f"Current data for game with packageName: {package_name}")
    print(json.dumps(game_data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder))

    if input("Would you like to update everything at once? (y/n): ").lower() == "y":
        game_data["developer"] = result["developer"]
        game_data["icon"] = result["icon"]
        game_data["banner"] = result["headerImage"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])
        game_data["genre"] = result["genre"]
        game_data["categories"] = [
            category["name"] for category in result["categories"]
        ]
    else:
        if input("Would you like to update the developer? (y/n): ").lower() == "y":
            game_data["developer"] = result["developer"]

        if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
            game_data["icon"] = result["icon"]

        if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
            game_data["banner"] = result["headerImage"]

        if input("Would you like to update the description? (y/n): ").lower() == "y":
            game_data["description"] = result["summary"]

        if input("Would you like to update the price? (y/n): ").lower() == "y":
            game_data["price"] = float(result["price"])

        if input("Would you like to update the genre? (y/n): ").lower() == "y":
            game_data["genre"] = result["genre"]

        if input("Would you like to update the categories? (y/n): ").lower() == "y":
            game_data["categories"] = [
                category["name"] for category in result["categories"]
            ]

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [
            int(tag)
            for tag in input(
                "Enter the new tags (comma-separated, without space): "
            ).split(",")
        ]

    db.collection("games").document(package_name).update(game_data)
    print("Game updated successfully")


# ---------------- 5. UPDATE ALL GAMES FROM SCRAPER (COSTLY) ----------------
def update_games_from_scraper():
    docs = db.collection("games").stream()

    for doc in docs:
        game_data = doc.to_dict()
        package_name = doc.id

        try:
            result = app(package_name, country="us", lang="en")
        except Exception as e:
            print(f"Skipping game with packageName {package_name} due to error: {e}")
            continue

        game_data["id"] = package_name

        if game_data["banner"].startswith("https://play-lh.googleusercontent.com"):
            game_data["banner"] = result["headerImage"]

        game_data["developer"] = result["developer"]
        game_data["icon"] = result["icon"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])
        game_data["genre"] = result["genre"]
        game_data["categories"] = [
            category["name"] for category in result["categories"]
        ]

        db.collection("games").document(package_name).update(game_data)
        print(f"Updated game with packageName: {package_name}")

    print("Games updated successfully")


# ---------------- 6. DELETE CERTAIN GAMES ----------------
def delete_games():
    package_names = input(
        "Enter the package names to delete (comma-separated, without space): "
    ).split(",")

    for package_name in package_names:
        package_name = package_name.strip()
        genre = None

        if genre is not None:
            if genre.lower() == "role playing":
                genre_doc_name = "rolePlaying"
            else:
                genre_doc_name = genre.lower()

            db.collection("gameIds").document(genre_doc_name).update(
                {"idsList": firestore.ArrayRemove([package_name])}
            )
            db.collection("gameIds").document("all").update(
                {"idsList": firestore.ArrayRemove([package_name])}
            )
            db.collection("games").document(package_name).delete()
            print(f"Deleted game with packageName: {package_name}")

    print("Games deleted successfully")


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
            "description": app_details.get("summary"),
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


# ---------------- 8. SHOW TAGS MEANING ----------------
def show_tags_meaning():
    print(
        "1: Subscription service\n2: Micro-transactions\n3: Battle pass\n4: Loot boxes\n5: Pay to win\n6: Malicious practices\n7: Concerning TOS\n8: Fake engagement\n9: Not as advertised\n10: Immoral developers\n11: Scam"
    )


# ---------------- 9. CREATE GENRE DOCUMENTS ----------------
def create_genre_documents():
    collection_name = "gameIds"
    doc_names = (
        "action,adventure,arcade,board,card,casual,educational,music,puzzle,racing,role playing,simulation,sports,strategy,trivia,word"
    ).split(",")
    array_name = "idsList"
    collection_ref = db.collection(collection_name)

    for doc_name in doc_names:
        doc_name = doc_name.strip()
        doc_ref = collection_ref.document(doc_name)
        doc_ref.set({array_name: [""]})
        print(f"Document '{doc_name}' created in '{collection_name}' collection.")

    print("Genre documents created successfully")


# ---------------- 10. POPULATE GENRE DOCUMENTS ----------------
def populate_genre_documents():
    collection_name = "gameIds"
    array_name = "idsList"
    collection_ref = db.collection(collection_name)

    for doc in collection_ref.stream():
        doc_ref = collection_ref.document(doc.id)
        array_values = input(
            f"Enter the array values to put in '{doc.id}' (comma-separated, without space): "
        )
        values_list = array_values.split(",")

        if values_list[0] != "":
            doc_ref.update({array_name: values_list})
            print(f"Document '{doc.id}' updated with '{array_name}' = {values_list}")
        else:
            print(f"Document '{doc.id}' not updated")
            continue


# ---------------- MAIN ----------------
def main():
    while True:
        print("Options:")
        print("1. Add a game using console")
        print("2. Add a game using scraper")
        print("3. Update a game using console")
        print("4. Update a game using scraper")
        print("5. Update all games using scraper (costly)")
        print("6. Delete certain games")
        print("7. Search for a game")
        print("8. Show tags meaning")
        print("9. Create genre documents (old)")
        print("10. Populate genre documents (old)")
        print("11. Exit")

        option = input("Select an option: ")
        if option == "1":
            package_name = input("Enter the package name: ")
            add_game_from_input(package_name)
        elif option == "2":
            package_name = input("Enter the package name: ")
            add_game_from_scraper(package_name)
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
        elif option == "7":
            search_game()
        elif option == "8":
            show_tags_meaning()
        elif option == "9":
            create_genre_documents()
        elif option == "10":
            populate_genre_documents()
        elif option == "11":
            break
        else:
            print("Invalid option. Please try again.")

        print()


if __name__ == "__main__":
    main()
