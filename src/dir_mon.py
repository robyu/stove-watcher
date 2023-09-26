import os
from pathlib import Path

class DirMon:
    def __init__(self, ftp_dir, # directory to monitor
                    holding_dir # directory to move files to if filename meets "hold" criteria
                 ):
        self.ftp_dir = Path(ftp_dir)
        assert self.ftp_dir.exists(), f"FTP directory {self.ftp_dir} does not exist"

        self.holding_dir = Path(holding_dir)
        assert self.holding_dir.exists(), f"Holding directory {self.holding_dir} does not exist"

    def _filter_reserve_files(self, files_l):
        """ 
        if the filename looks like "hold_*.*" then move it the holding directory
        and remove it from the list of files 
        """
        for f in files_l:
            if f.startswith('hold-'):
                # move the file to the holding directory
                os.rename(self.ftp_dir / f, self.holding_dir / f)
                # remove the file from the list of files
                files_l.remove(f)
        return files_l
    
    def get_new_files(self):
        # Get a list of all files in the FTP directory that match "*.png" or "*.jpg" or "*.jpeg"
        files_l = [f for f in os.listdir(self.ftp_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        files_l = self._filter_reserve_files(files_l)

        # Return the list of new files
        return list(files_l)
    