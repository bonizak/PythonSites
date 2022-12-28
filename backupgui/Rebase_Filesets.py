import os

import psycopg2

from CommonDB import CommonDB as db_services
from CommonOs import OsServices as os_services

from .models import BaseFileSets


class RebaseFileSets(db_services, os_services):
    """
        This class contains the methods to collect and create a list of all directories, to the depth of directories
        as provided, under the supplied list of file systems' roots.
        It will then update a table of Base file path 'INCLUDES'.

    Args
        Required: none
        Optional: none

    Logging: INFO | WARN | ERROR

    """

    __author__ = "Barry Onizak"
    __version__ = "20220418.1"

    # # # # # End of header # # # #

    def Build_FileSets(self):
        """
        This method starts the process to read a table of RootPaths and scan them for sub-directories and files,
        then writing these files and folders into the BaseFileSets table.
        :return:
        """
        dbConn = db_services.dbConnect(self)
        RootPathRows = []
        RootPathsIn = self.dbGetRootPaths(dbConn)
        for index in range(len(RootPathsIn)):
            rpPath = ""
            rpDepth = 1
            rpFileFolder = ""

            for key in RootPathsIn[index]:
                if key == "RootPath":
                    rpPath = RootPathsIn[index][key]
                elif key == "Max_Depth":
                    rpDepth = RootPathsIn[index][key]
                elif key == "FilesFolders":
                    rpFileFolder = RootPathsIn[index][key]

                if len(rpPath) > 0:
                    for dirpath, subdirList, filesList in self.walkLevel(rpPath, rpDepth):
                        if rpDepth == 0:
                            ''' empty scan '''
                            pass
                        elif rpDepth == -1:
                            ''' collect the files in the RootFileSystem directory and all subdirectories'''
                            if rpFileFolder in ("Folders", "Both"):
                                for subdir in subdirList:
                                    if os.path.join(dirpath, subdir).find("Trash") == -1 and \
                                            os.path.join(dirpath, subdir).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, subdir)):
                                        RootPathRows.append(
                                            {"FileSetName": "ToBeUpdated",
                                             "Includes": os.path.join(dirpath, subdir),
                                             "Excludes": "NA", "Compress": "YES", "Recursive": "Yes"})
                            if rpFileFolder in ("Files", "Both"):
                                for file in filesList:
                                    if os.path.join(dirpath, file).find("Trash") == -1 and \
                                            os.path.join(dirpath, file).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, file)):
                                        RootPathRows.append(
                                            {"FileSetName": "ToBeUpdated",
                                             "Includes": os.path.join(dirpath, file),
                                             "Excludes": "NA", "Compress": "YES", "Recursive": "No"})
                        elif rpDepth == os.path.abspath(rpPath).count(os.path.sep):
                            ''' collect the files and directories ONLY in the RootFileSystem - no recursive scan'''
                            if rpFileFolder in ("Folders", "Both"):
                                for subdir in subdirList:
                                    if os.path.join(dirpath, subdir).find("Trash") == -1 and \
                                            os.path.join(dirpath, subdir).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, subdir)):
                                        if os.path.join(dirpath, subdir).count(os.path.sep) <= rpDepth:
                                            RootPathRows.append(
                                                {"FileSetName": "ToBeUpdated",
                                                 "Includes": os.path.join(dirpath, subdir),
                                                 "Excludes": "NA", "Compress": "YES", "Recursive": "No"})
                            if rpFileFolder in ("Files", "Both"):
                                for file in filesList:
                                    if os.path.join(dirpath, file).find("Trash") == -1 and \
                                            os.path.join(dirpath, file).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, file)):
                                        if os.path.join(dirpath, file).count(os.path.sep) == rpDepth + 1:
                                            RootPathRows.append(
                                                {"FileSetName": "ToBeUpdated",
                                                 "Includes": os.path.join(dirpath, file),
                                                 "Excludes": "NA", "Compress": "YES", "Recursive": "No"})
                        elif rpDepth >= os.path.abspath(rpPath).count(os.path.sep):
                            ''' collect the files and directories in the RootFileSystem - with recursive scan'''
                            if rpFileFolder in ("Folders", "Both"):
                                for subdir in subdirList:
                                    if os.path.join(dirpath, subdir).find("Trash") == -1 and \
                                            os.path.join(dirpath, subdir).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, subdir)):
                                        if os.path.join(dirpath, subdir).count(os.path.sep) <= rpDepth:
                                            RootPathRows.append(
                                                {"FileSetName": "ToBeUpdated",
                                                 "Includes": os.path.join(dirpath, subdir),
                                                 "Excludes": "NA", "Compress": "YES", "Recursive": "YES"})
                            if rpFileFolder in ("Files", "Both"):
                                for file in filesList:
                                    if os.path.join(dirpath, file).find("Trash") == -1 and \
                                            os.path.join(dirpath, file).find("lost+found") == -1 and \
                                            not os.path.islink(os.path.join(dirpath, file)):
                                        if os.path.join(dirpath, file).count(os.path.sep) == rpDepth + 1:
                                            RootPathRows.append(
                                                {"FileSetName": "ToBeUpdated",
                                                 "Includes": os.path.join(dirpath, file),
                                                 "Excludes": "NA", "Compress": "YES", "Recursive": "No"})

        if len(RootPathRows) == 0:
            print(f' Empty RootPath Scan Returned. Verify Max_Depth values in RootPath Sheet of workbook.'
                  f' \n Exiting!')

        sorted_RootPathRows = sorted(RootPathRows, key=lambda I: I["Includes"])
        self.update_BaseFileSets(dbConn, sorted_RootPathRows)
        return sorted_RootPathRows

    def update_BaseFileSets(self, dbConn, rootPaths):
        inserted_rows = 0
        try:
            for index in range(len(rootPaths)):
                for key in rootPaths[index]:
                    sql = f'INSERT INTO "public"."BaseFileSets" ' \
                          f'("FileSetName", "Includes", "Excludes", "Compress", "Recursive") ' \
                          f'VALUES (%s, %s, %s, %s, %s)'

                    cur = dbConn.cursor()
                    cur.execute(sql, (rootPaths[index]["FileSetName"], rootPaths[index]["Includes"],
                                      rootPaths[index]["Excludes"], rootPaths[index]["Compress"],
                                      rootPaths[index]["Recursive"]))
                    msg = f'Inserted {cur.rowcount} row.'
                    inserted_rows += cur.rowcount
                    os_services.debug(self, msg)
        except psycopg2.DatabaseError as err:
            os_services.debug(self, f"Error {err}")
        finally:
            dbConn.commit()
            cur.close()
            os_services.debug(self, f'Inserted {inserted_rows} rows')

    def walkLevel(self, rfs_path, max_depth):
        """
            This method takes a path and a max_depth value and
            walks the path to max_depth collecting and
            yielding directories and files
            :param rfs_path: Root File system to be scanned
            :param max_depth: Maximum directory depth to scan the path
            :return: yield tuples of max_depth, root, dirs[:], files
        """
        if max_depth == 0:  # return nothing
            return
        elif max_depth < 0:  # return everything
            for dirpath, dirnames, filenames in os.walk(rfs_path, followlinks=False):
                yield dirpath, dirnames[:], filenames
            return
        else:  # return only up to the max depth
            rfspath = str(rfs_path).rstrip(os.path.sep)  # strip of any ending pathsep
            if os.path.isdir(rfspath):
                rfspath_depth = rfspath.count(os.path.sep)
                for dirpath, dirnames, filenames in os.walk(rfspath, followlinks=False):
                    dirpath_depth = dirpath.count(os.path.sep)
                    yield dirpath, dirnames, filenames
                    if rfspath_depth + max_depth <= dirpath_depth:
                        del dirnames[:]
            else:
                os_services.error(self, f'Directory provided, {rfspath} is invalid')

    def dbGetRootPaths(self, dbConn):
        RootPaths = []
        try:
            cur = dbConn.cursor()
            sql = f'SELECT "rp"."ID", "rp"."Rootpath", "rp"."Max_Depth",  "rp"."FilesFolders" ' \
                  f'FROM "public"."RootPaths" "rp" ' \
                  f'ORDER BY "rp"."ID" ASC'

            cur.execute(sql)
            rowCount = cur.rowcount

            while rowCount > 0:
                rowData = cur.fetchone()
                row_set_dict = {"ID": rowData[0],
                                "RootPath": rowData[1],
                                "MaxDepth": rowData[2],
                                "FilesFolders": rowData[3]}
                RootPaths.append(row_set_dict)
                rowCount -= 1

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Error connecting to PostgreSQL {error}')
        finally:
            return RootPaths
