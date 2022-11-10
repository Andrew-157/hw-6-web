from aiopath import AsyncPath
import asyncio
import aioshutil
import os
from locale import normalize


async def edit_file(name, path, dir_address, subfolder):
    file = AsyncPath(path)
    splitted_name = name.split(".")
    new_name = normalize(name.replace(f'.{splitted_name[-1]}', ""))
    new_path_name = os.path.join(
        dir_address, f"{new_name}.{splitted_name[-1]}")
    await file.rename(new_path_name)
    to_move = os.path.join(dir_address, subfolder)
    await aioshutil.move(new_path_name, to_move)


def create_sub_folders(name):
    directories = ["images", "video", "documents", "archive", "audio"]
    for dir in directories:
        path = os.path.join(name, dir)
        os.mkdir(path)
    return directories


async def main(path):
    directories = create_sub_folders(path)
    path_obj = AsyncPath(path)
    futures = []

    async for file in path_obj.iterdir():
        if file.name in directories:
            continue
        if await file.is_dir():

            dir = os.listdir(file)
            if not dir:
                os.rmdir(file)

            else:
                futures.append(main(file))

        elif file.name.endswith(('.jpeg', '.png', '.jpg', '.svg')):
            futures.append(edit_file(file.name, file, path_obj, "images"))

        elif file.name.endswith(('.avi', '.mp4', '.mov', '.mkv')):
            futures.append(edit_file(file.name, file, path_obj, "video"))

        elif file.name.endswith(('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx')):
            futures.append(edit_file(file.name, file, path_obj, "documents"))

        elif file.name.endswith(('.mp3', '.ogg', '.wav', '.amr')):
            futures.append(edit_file(file.name, file, path_obj, "audio"))

        elif file.name.endswith(('.zip', 'gz', '.tar')):
            splitted_name = file.name.split(".")
            new_name = normalize(file.name.replace(
                f".{splitted_name[-1]}", ""))
            sub_archives = os.path.join(path_obj, "archive")
            new_folder = os.path.join(sub_archives, new_name)
            os.mkdir(new_folder)
            await aioshutil.unpack_archive(file, new_folder)
            os.remove(file)
            futures.append(main(os.path.join(new_folder, "archive")))

    await asyncio.gather(*futures)


asyncio.run(main("C:\\Users\\Андрей\\Desktop\\train_dir"))
