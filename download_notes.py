import canvasapi
import os
import pickle
import pathlib

WINDOWS = os.name == "nt"

download_location = str(
    input(
        "Enter the path to the folder you want to download to (or nothing to download to current directory): \n"
    )
)
if not download_location:
    download_location = os.getcwd()

# get user data from pickle file if it exists, otherwise create it
try:
    with open("user_data.pickle", "rb") as f:
        BASE_URL, ACCESS_TOKEN = pickle.load(f)

except FileNotFoundError:
    with open("user_data.pickle", "wb") as f:
        while True:
            BASE_URL = str(input("Enter your Canvas URL: "))
            ACCESS_TOKEN = str(input("Enter your Canvas access token: "))
            if BASE_URL and ACCESS_TOKEN:
                pickle.dump((BASE_URL, ACCESS_TOKEN), f, pickle.HIGHEST_PROTOCOL)
                break
            print("Invalid input. Try again.")

canvas = canvasapi.Canvas(BASE_URL, ACCESS_TOKEN)

course_ids = {
    str(course_id): course for course_id, course in enumerate(canvas.get_courses())
}

print("\nCourses:")
for i in course_ids:
    print(f"Course number: {i}, Course name: {course_ids[i]}")

chosen_courses = [
    course_ids[i]
    for i in str(
        input(
            "Enter the course numbers you want to download files from seperated by commas: \n"
        )
    ).split(", ")
]

# user chooses courses, then chooses folders from those courses
# chosen_folders = {course: [folder1, folder2, ...], course2: [folder1, folder2, ...]}
# with each folder being a canvasapi object that can be used to download files
chosen_folders = []
for course in chosen_courses:
    print(f"Folders for {course}: ")
    course_folders = []
    download_all = False
    if str(input("Download all folders? (y/n)")).lower() == "y":
        download_all = True
    for folder in course.get_folders():
        if download_all:
            course_folders.append(folder)
        else:
            print(f"Folder: {folder.name}")
            if str(input("Download folder? (y/n)")).lower() == "y":
                course_folders.append(folder)
                print(f"{folder.name} added to download list.\n")

    chosen_folders.append({course: course_folders})

download_count = 0
for folder in chosen_folders:
    for course, course_folders in folder.items():
        parent_dir = pathlib.PurePosixPath(f"{download_location}", f"{course}")
        if WINDOWS:
            parent_dir = pathlib.PureWindowsPath(f"{download_location}", f"{course}")
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)

        for folder in course_folders:
            print(f"Downloading {folder.name} from {course}.")
            folder_path = os.path.join(parent_dir, folder.name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            for file in folder.get_files():
                file_name = str(file.filename).replace("+", " ")
                file_path = os.path.join(folder_path, file_name)
                if os.path.exists(file_path):
                    update = str(
                        input(f"{file_name} already exists. Update? (y/n)")
                    ).lower()
                    if update == "y":
                        file.download(file_path)
                        download_count += 1
                    continue

                else:
                    file.download(file_path)
                    download_count += 1


print(f"Download complete. {download_count} files downloaded.")
