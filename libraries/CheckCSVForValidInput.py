from robot.api import logger
from urllib.error  import URLError
from urllib.request import urlopen
from RPA.Crypto import Hash
from RPA.Crypto import Crypto
from RPA.Robocorp.Vault import Vault



class CheckCSVForValidInput:
    def __init__(self, csv_location: str, http_ressource=False) -> None:
        self.csv_location = csv_location
        self.http_ressource = http_ressource

    def download_csv_file(self):
        if self.http_ressource:
            try:
                with urlopen(self.csv_location) as f:
                    self.csv_data = f.read(512)
            except URLError:
                logger.error("Downloading failed. Check Link: " + self.csv_location)
        else:
            try:
                with open(self.csv_location, "rb") as f:
                    self.csv_data = f.read()
            except FileNotFoundError:
                logger.error("File not existent or opening error.")

    def validate_csv_header(self):
        self.csv_lines = self.csv_data.splitlines()
        assert self.csv_lines[0] == b"Order number,Head,Body,Legs,Address"

    def validate_csv_data(self):
        assert (self.csv_data.replace(b",",b"").replace(b" ",b"").replace(b"\n",b"").isalnum())

        for i in range(1, len(self.csv_lines)):
            columns = self.csv_lines[i].split(b",")
            try:
                [int(columns[j]) for j in range(4)]
            except ValueError:
                logger.error("Casting to Integer failed. Check CSV.")
            assert int(columns[0]) == i
            assert all([int(columns[j]) in range(1,7) for j in [1, 2, 3]])
            assert len(columns[4]) < 40

    def save_csv_to_disk(self):
        hash =  Crypto()
        self.csv_hash = hash.hash_string(self.csv_data, method=Hash.SHA3_224)
        try:
            with open(self.csv_hash, "wb") as f:
                f.write(self.csv_data)
            logger.info("CSV File Written to disk with name: " + self.csv_hash)
        except OSError:
            logger.error("Writing of CSV File to disk failed.")
    
    def get_csv_hash_value(self):
        self.download_csv_file()
        self.validate_csv_header()
        self.validate_csv_data()
        self.save_csv_to_disk()
        
        csv_vault = Vault().get_secret("orderdata")
        csv_vault["csvhash"] = self.csv_hash
        Vault().set_secret(csv_vault)

        

# Check_CSV_For_Valid_Input("https://robotsparebinindustries.com/orders.csv", True)
