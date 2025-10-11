import CONFIG
from logger import logger
from pathlib import Path
import zipfile, os


class Compressor:
    """
    Compresses a given folder into a ZIP archive using only standard libraries.

    Attributes:
        input_path (Path): Path to the folder to be compressed.
    """

    def __init__(self, input_path):
        """
        Initialize the Compressor instance.

        Logs initialization if debugging is enabled.
        """
        if CONFIG.DEBUG.get("compressor", True):
            logger.log("compressor", "Initialized Compressor", level="DEBUG")
        
        self.input_path = Path(input_path)

    def __zip_folder(self):
        """
        Create a ZIP archive from the input folder.

        - Recursively walks through all subfolders and files.
        - Maintains the relative folder structure inside the archive.
        - The archive is saved next to the input folder with `.zip` extension.
        """
        folder_path = self.input_path
        zip_path = self.input_path.with_suffix(".zip")

        if CONFIG.DEBUG.get("compressor", True):
            logger.log("compressor", f"Compressing {folder_path} → {zip_path}", level="DEBUG")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(folder_path)
                    zipf.write(file_path, arcname)

        if CONFIG.DEBUG.get("compressor", True):
            logger.log("compressor", f"Compression complete: {zip_path}", level="DEBUG")

    def run_compressor(self):
        """
        Public method to start the compression process.
        """
        self.__zip_folder()
