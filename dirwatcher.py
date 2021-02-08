import os
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class DirectoryWatcher():

    """Watch a directory for new files and pass them on to the job handler"""

    # File validation
    FILE_TYPES = {"*.gif", "*.heic", "*.heif", "*.jpg", "*.pdf", "*.png",
        "*.GIF", "*.HEIC", "*.HEIF", "*.JPG", "*.PDF", "*.PNG"}
    
    current_files = set()

    def __init__(self):
        pass

    def current_files_in_dir(self, path):
        # Not implemented
        files = os.listdir(path)
        for file in files:
            self.current_files.add(file)
        print(self.current_files)

    def create_event_handler(self, path):

        patterns = self.FILE_TYPES
        ignore_patterns = ""
        ignore_dirs = True
        case_sensitive = True

        event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_dirs, case_sensitive)

        return event_handler