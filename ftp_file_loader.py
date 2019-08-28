import os
import ftplib
from zipfile import ZipFile

class FTPFileLoader:
    def __init__(self, ftp_host, ftp_cwd, ftp_user, ftp_password, data_path):
        self.ftp_host = ftp_host
        self.ftp_cwd = ftp_cwd
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.data_path = data_path

        self.ftp_connection = ftplib.FTP(self.ftp_host, self.ftp_user, self.ftp_password)
        self.ftp_connection.cwd(self.ftp_cwd)
    
    # loads first file from the server that starts with "filename"
    # this allows to load a file without knowing its full name.
    # returns False when file wasn't found
    def load_file_starts_with(self, filename):
        downloaded_filename = ""
        for data_filename in self.ftp_connection.nlst():
            downloaded_filename = self.data_path + data_filename
            if data_filename.startswith(filename):    
                return self.load_file(data_filename, downloaded_filename)
        return False
    
    # load file by exact filename and return its filename
    def load_file(self, filename_remote, filename_local):
        if not os.path.isfile(filename_local):
            with open(filename_local, "wb") as f:
                self.ftp_connection.retrbinary("RETR " + filename_remote, f.write)
                print("INFO: saved " + filename_remote + " into " + filename_local)
                return filename_local
        return filename_local
