import os 
import time
import threading
import re
from typing import Callable,Dict
from logging import Logger

class WatchDirectoryError(Exception):
    pass

class PyFileWatcher:
    def __init__(self, dir_path: str, file_pattern: str, file_modified_callback: Callable[[str], None], file_created_callback: Callable[[str], None], file_deleted_callback: Callable[[str], None]) -> None:
        """Initialize the PyFileWatcher object with the given parameters.

        Args:
            dir_path (str): The path of the directory to watch.
            file_pattern (str): A regular expression pattern to match file names.
            file_modified_callback (Callable[[str], None]): A function to call when a file is modified.
            file_created_callback (Callable[[str], None]): A function to call when a file is created.
            file_deleted_callback (Callable[[str], None]): A function to call when a file is deleted.
            logger (Logger): Logger object to use for logging.
        """
        self.dir_path = dir_path
        self.file_pattern = file_pattern
        self.file_modified_callback = file_modified_callback
        self.file_created_callback = file_created_callback
        self.file_deleted_callback = file_deleted_callback
        self.stop_watching = False
        
        if not os.path.exists(dir_path):
            raise WatchDirectoryError(f"Directory {dir_path} does not exist.")
        if not os.path.isdir(dir_path):
            raise WatchDirectoryError(f"Path {dir_path} is not a directory.")
        if not re.match(file_pattern, ""):
            raise WatchDirectoryError(f"File pattern {file_pattern} is not valid.")
        pass

    def stop(self) -> None:
        """Stops watching the directory.
        """
        self.stop_watching = True
    
    def watch(self) -> None:
        """Starts watching the directory.
        """
        #info logger
        files = self.get_files()
        while not self.stop_watching:
            time.sleep(1)
            print(".", end="",flush=True)
            self.check_for_deleted_files(files)
            self.check_for_modified_files(files)
            self.check_for_new_files(files)
         
    
    def get_files(self) -> Dict[str, float]:
        """Returns a dictionary of file names and their modification times.

        Returns:
            Dict[str, float]: A dictionary of file names and their modification times.
        """
        files = {}
        for file_name in os.listdir(self.dir_path):
            if re.match(self.file_pattern, file_name):
                # files[file_name] = os.path.getmtime(os.path.join(self.dir_path, file_name))
                file_path = os.path.join(self.dir_path, file_name)
                # files[file_name] = os.path.getmtime(file_path)
                files[file_name] = os.stat(file_path).st_mtime
        return files

    def check_for_deleted_files(self, files: Dict[str, float]) -> None:
        """Checks if any files have been deleted.

        Args:
            files (Dict[str, float]): A dictionary of file names and their modification times.
        """
        for file_path, last_modified in list(files.items()):
            if not os.path.exists(file_path):
                del files[file_path]    
                t = threading.Thread(target=self.file_deleted_callback, args=(file_path,))
                t.start()
    
    def check_for_modified_files(self, files: Dict[str, float]) -> None:
        """Checks if any files have been modified.

        Args:
            files (Dict[str, float]): A dictionary of file names and their modification times.
        """
        for file_path, last_modified in list(files.items()):
            current_modified = os.stat(file_path).st_mtime
            # current_modified = os.getmtime(file_path)
            if current_modified != last_modified:
                files[file_path] = current_modified
                t = threading.Thread(target=self.file_modified_callback, args=(file_path,))
                t.start()
    
    def check_for_new_files(self, files: Dict[str, float]) -> None:
        """Checks if any new files have been created.

        Args:
            files (Dict[str, float]): A dictionary of file names and their modification times.
        """
        for file_name in os.listdir(self.dir_path):
            # if re.match(self.file_pattern, file_name) and file_name not in files:
            if re.match(self.file_pattern, file_name):
                file_path = os.path.join(self.dir_path, file_name)
                if file_path not in files:
                    files[file_path] = os.stat(file_path).st_mtime
                    t = threading.Thread(target=self.file_created_callback, args=(file_path,))
                    t.start()