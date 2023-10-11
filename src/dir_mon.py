import os
from pathlib import Path
import datetime

class DirMon:
    def __init__(self, ftp_dir, # directory to monitor
                    holding_dir, # directory to move files to if filename meets "hold" criteria
                    timeout_sec = 5
                 ):
        self.ftp_dir = Path(ftp_dir)
        assert self.ftp_dir.exists(), f"FTP directory {self.ftp_dir} does not exist"

        self.holding_dir = Path(holding_dir)
        assert self.holding_dir.exists(), f"Holding directory {self.holding_dir} does not exist"

        self.timeout_sec = timeout_sec

    def _filter_reserve_files(self, files_l):
        """ 
        if the filename looks like "hold_*.*" then move it the holding directory
        and remove it from the list of files 
        """
        hold_files_l = []
        for f in files_l:
            if f.name.startswith('hold-'):
                # define hold_f with the same base filename but with a path defined by self.holding_dir
                hold_f = self.holding_dir / f.name
                # move the file to the holding directory
                f.rename(hold_f)
                # append hold_f to hold_files_l
                hold_files_l.append(hold_f)
                # remove the file from the list of files
                files_l.remove(f)
        return files_l, hold_files_l
    
    def get_new_files(self):
        """
        monitors a directory for new files

        returns:
            a dictionary with two keys:
                new_files: a list of file paths that are new
                hold_files: a list of file paths that are being held
        """
        now_dt = datetime.datetime.now()
        found_files = False

        while not found_files and (datetime.datetime.now() - now_dt).seconds < self.timeout_sec:
            # Get a list of all files in the FTP directory that match "*.png" or "*.jpg" or "*.jpeg"
            files_l = [(self.ftp_dir / f).resolve() for f in os.listdir(self.ftp_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

            if len(files_l) > 0:
                found_files = True
            #
        #

        # if any files are for the holding directory, then move them there
        files_l, hold_files_l = self._filter_reserve_files(files_l)

        d = {'new_files': files_l, 'hold_files': hold_files_l}
        return d
    