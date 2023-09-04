import firebase_admin
from firebase_admin import credentials, firestore
from google_play_scraper import app
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
cred = credentials.Certificate(
    "rayvue-app-firebase-adminsdk-e1e3m-d4c0bef170.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# ---------------- ADD A GAME FROM INPUT ----------------
def add_game_from_input():
    game_data = {}
    game_data["id"] = db.collection("games").document().id
    game_data["packageName"] = input("Enter the package name: ")
    game_data["name"] = input("Enter the game name: ")
    game_data["icon"] = input("Enter the icon URL: ")
    game_data["banner"] = input("Enter the banner URL: ")
    game_data["description"] = input("Enter the description: ")
    game_data["price"] = float(input("Enter the price: "))
    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = [int(tag)
                         for tag in tags_input.split(",")] if tags_input else []
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP

    db.collection("games").document(game_data["id"]).set(game_data)
    print("Game added successfully")


# ---------------- ADD A GAME FROM SCRAPER AND INPUT ----------------
def add_game_from_scraper():
    game_data = {}
    game_data["id"] = db.collection("games").document().id
    game_data["packageName"] = input("Enter the package name: ")
    result = app(game_data["packageName"], country="us", lang="en")
    game_data["name"] = result["title"]
    game_data["icon"] = result["icon"]
    if input("Would you like to scrape the banner? (y/n): ").lower() == "y":
        game_data["banner"] = result["headerImage"]
    else:
        game_data["banner"] = input("Enter the banner URL: ")
    game_data["description"] = result["summary"]
    game_data["price"] = float(result["price"])
    tags_input = input("Enter the tags (comma-separated, without space): ")
    game_data["tags"] = [int(tag)
                         for tag in tags_input.split(",")] if tags_input else []
    game_data["dateAdded"] = firestore.SERVER_TIMESTAMP

    db.collection("games").document(game_data["id"]).set(game_data)
    print("Game added successfully")


# ---------------- UPDATE A GAME FROM INPUT ----------------
def update_game_from_input(package_name):
    doc_ref = (
        db.collection("games").where(
            "packageName", "==", package_name).limit(1).get()
    )
    if not doc_ref:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref[0].to_dict()

    print(f"Current data for game with packageName: {package_name}")
    print(game_data)

    if input("Would you like to update the packageName? (y/n): ").lower() == "y":
        game_data["packageName"] = input("Enter the new packageName: ")

    if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
        game_data["banner"] = input("Enter the new banner URL: ")

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [int(tag) for tag in input(
            "Enter the new tags (comma-separated, without space): ").split(",")]

    if input("Would you like to update the name? (y/n): ").lower() == "y":
        game_data["name"] = input("Enter the new name: ")

    if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
        game_data["icon"] = input("Enter the new icon URL: ")

    if input("Would you like to update the description? (y/n): ").lower() == "y":
        game_data["description"] = input("Enter the new description: ")

    if input("Would you like to update the price? (y/n): ").lower() == "y":
        game_data["price"] = float(input("Enter the new price: "))

    db.collection("games").document(doc_ref[0].id).update(game_data)
    print("Game updated successfully")


# ---------------- UPDATE A GAME FROM SCRAPER AND INPUT ----------------
def update_game_from_scraper(package_name):
    doc_ref = (
        db.collection("games").where(
            "packageName", "==", package_name).limit(1).get()
    )
    if not doc_ref:
        print(f"No game found with packageName: {package_name}")
        return

    game_data = doc_ref[0].to_dict()

    print(f"Current data for game with packageName: {package_name}")
    print(game_data)

    if input("Would you like to update the banner URL? (y/n): ").lower() == "y":
        if game_data["banner"].startswith("https://play-lh.googleusercontent.com"):
            result = app(package_name, country="us", lang="en")
            game_data["banner"] = result["headerImage"]
        else:
            game_data["banner"] = input("Enter the new banner URL: ")

    if input("Would you like to update the tags? (y/n): ").lower() == "y":
        game_data["tags"] = [int(tag) for tag in input(
            "Enter the new tags (comma-separated, without space): ").split(",")]

    if input("Would you like to update the packageName? (y/n): ").lower() == "y":
        package_name_input = input("Enter the new packageName: ")
        result = app(package_name_input, country="us", lang="en")
        game_data["packageName"] = package_name_input
        package_name = package_name_input
        game_data["name"] = result["title"]
        game_data["icon"] = result["icon"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])
    else:
        if input("Would you like to update the name? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["name"] = result["title"]

        if input("Would you like to update the icon URL? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["icon"] = result["icon"]

        if input("Would you like to update the description? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["description"] = result["summary"]

        if input("Would you like to update the price? (y/n): ").lower() == "y":
            result = app(package_name, country="us", lang="en")
            game_data["price"] = float(result["price"])

    db.collection("games").document(doc_ref[0].id).update(game_data)
    print("Game updated successfully")


# ---------------- UPDATE ALL GAMES FROM SCRAPER ----------------
def update_games_from_scraper():
    docs = db.collection("games").stream()

    for doc in docs:
        game_data = doc.to_dict()
        package_name = game_data["packageName"]

        try:
            result = app(package_name, country="us", lang="en")
        except Exception as e:
            print(
                f"Skipping game with packageName: {package_name} due to error: {e}")
            continue

        if game_data["banner"].startswith("https://play-lh.googleusercontent.com"):
            game_data["banner"] = result["headerImage"]
        game_data["name"] = result["title"]
        game_data["icon"] = result["icon"]
        game_data["description"] = result["summary"]
        game_data["price"] = float(result["price"])

        db.collection("games").document(doc.id).update(game_data)
        print(f"Updated game with packageName: {package_name}")

    print("Games updated successfully")


# ---------------- DELETE CERTAIN GAMES ----------------
def delete_games():
    package_names = input(
        "Enter the package names to delete (comma-separated, without space): ").split(",")

    for package_name in package_names:
        package_name = package_name.strip()
        docs = db.collection("games").where(
            "packageName", "==", package_name).stream()

        for doc in docs:
            db.collection("games").document(doc.id).delete()
            print(f"Deleted game with packageName: {package_name}")

    print("Game deleted successfully")


# ---------------- SHOW ALL GAMES ----------------
def list_games():
    docs = db.collection("games").stream()

    for doc in docs:
        game = doc.to_dict()
        print(f"Name: {game['name']}, PackageName: {game['packageName']}")

    print("Games listed successfully")


# ---------------- MAIN ----------------
def main():
    while True:
        print("Options:")
        print("1. Add a game from the console")
        print("2. Add a game from the scraper")
        print("3. Update a game from the console")
        print("4. Update a game from the scraper")
        print("5. Update all games from the scraper")
        print("6. Delete certain games")
        print("7. List all games")
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
        elif option == "7":
            list_games()
        elif option == "8":
            break
        else:
            print("Invalid option. Please try again.")

        print()


if __name__ == "__main__":
    main()
