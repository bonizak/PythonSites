import os.path
import inspect
import psycopg2
from configparser import ConfigParser
from CommonOs import OsServices as os_services


class CommonDB(os_services):
    """
    This class contains the methods to read the PostgreSQL BackupListDB and
    populate the arrays of dictionaries for each table

    Args
        Required: none
        Optional: none

    Alerts: Critical | WARN | ERROR

    Logging: none

    """

    __author__ = "Barry Onizak"
    __version__ = "20220410.1"

    # # # # # End of header # # # #
    BackupSet_AoD = []
    StorageSet_AoD = []
    FileSet_AoD = []
    Frequency_AOD = []
    AppConfig_AOD = []

    def __init__(self):
        super().__init__()

    def dbSetsCollect(self):

        dbConn = self.dbConnect()
        self.BackupSet_AoD = self.dbGetBackupSets(dbConn)
        self.StorageSet_AoD = self.dbGetStorageSets(dbConn)
        self.FileSet_AoD = self.dbGetFileSets(dbConn)
        self.Frequency_AOD = self.dbGetFrequency(dbConn)
        # self.AppConfig_AOD = self.dbAppConfig(dbConn)
        return self.BackupSet_AoD, self.StorageSet_AoD, self.FileSet_AoD, self.Frequency_AOD, self.AppConfig_AOD

    def dbConnect(self):

        curFrame = inspect.currentframe()
        calFrame = inspect.getouterframes(curFrame, 2)
        os_services.debug('Connect to DB caller name:', calFrame[1][3])
        """ Connect to the PostgreSQL database server """
        resource_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resource")
        dbConn = None

        try:
            # read connection parameters
            params = self.dbParser(os.path.join(resource_path, 'database.ini'), 'postgresql')
            dbConn = psycopg2.connect(**params)

            # create a cursor
            cur = dbConn.cursor()
            cur.execute("SELECT current_database()")
            os_services.debug(f'Current database name {cur.fetchone()[0]}')

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            os_services.critical(f'Error connecting to PostgreSQL {error}')
            return None
        finally:
            return dbConn

    def dbGetBackupSets(self, dbConn):
        try:
            cur = dbConn.cursor()
            sql = f'SELECT "b"."ID", "b"."BackupSetName", "b"."Versions", ' \
                  f' "b"."StorageSetID", ' \
                  f' "b"."FileSetID", ' \
                  f' "b"."FrequencyID" ' \
                  f'FROM "public"."BackupSets" "b" ' \
                  f'ORDER BY "b"."ID" ASC'

            # f' INNER JOIN "public"."StorageSets" "s" on "b"."StorageSetID" = "s"."ID" ' \
            # f' INNER JOIN "public"."FileSets" "f" on "b"."FileSetID" = "f"."ID" ' \
            # f' INNER JOIN "public"."Frequencies" "q" on "b"."FrequencyID" = "q"."ID" ' \
            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0], "BackupSetName": rowData[1], "Versions": rowData[2],
                                "StorageSetID": rowData[3], "FileSetID": rowData[4], "FrequencyID": rowData[5]}
                self.BackupSet_AoD.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return self.BackupSet_AoD

    def dbGetStorageSets(self, dbConn):
        try:
            cur = dbConn.cursor()
            sql = f'SELECT "s"."ID", "s"."StorageSetname", "s"."StoragePath", "s"."DevicePathId" ' \
                  f'FROM "public"."StorageSets" "s" ' \
                  f'ORDER BY "s"."ID" ASC'

            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0], "StorageSetName": rowData[1], "StorageSetPath": rowData[2],
                                "DevicePathID": rowData[3]}
                self.StorageSet_AoD.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return self.StorageSet_AoD

    def dbGetFileSets(self, dbConn):
        try:
            cur = dbConn.cursor()
            sql = f'SELECT "f"."ID", "f"."FileSetName", ' \
                  f'"f"."Includes", "f"."Excludes", ' \
                  f'"f"."Compress", "f"."Recursive", "f"."EstimatedSize" ' \
                  f'FROM "public"."FileSets" "f"  ' \
                  f'ORDER BY "f"."ID" ASC'

            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0], "FileSetName": rowData[1],
                                "Includes": rowData[2], "Excludes": rowData[3],
                                "Compress": rowData[4],  "Recursive": rowData[5],  "EstimatedSize": rowData[6]}
                self.FileSet_AoD.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return self.FileSet_AoD

    def dbGetFrequency(self, dbConn):
        try:
            cur = dbConn.cursor()
            sql = f'SELECT "q"."ID", "q"."Frequency" ' \
                  f'FROM "public"."Frequencies" "q"  ' \
                  f'ORDER BY "q"."ID" ASC'

            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0], "Frequency": rowData[1]}
                self.Frequency_AOD.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return self.Frequency_AOD

    def dbGetAppConfig(self, dbConn, key_id):
        try:
            cur = dbConn.cursor()
            sql = f'SELECT Id, key, value ' \
                  f'FROM "public"."AppConfig" "ap" ' \
                  f'WHERE "ap"."key" = {key_id} ' \
                  f'ORDER BY "ap"."ID" ASC'

            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0], "Key": rowData[1], "Value": rowData[2]}
                self.AppConfig_AOD.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return self.AppConfig_AOD

    def dbParser(self, filename, section):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('B Section {0} not found in the {1} file'.format(section, filename))

        return db

    @staticmethod
    def getCaller():
        curFrame = inspect.currentframe()
        calFrame = inspect.getouterframes(curFrame, 2)
        print('caller name:', calFrame[1][3])
