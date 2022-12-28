import psutil
from django.db import connection
from django.db import models


class StorageSets(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    StorageSetName = models.CharField(max_length=48)
    StoragePath = models.CharField(max_length=1024)
    DevicePathID = models.ForeignKey('DeviceTypes', on_delete=models.CASCADE)

    class Meta:
        db_table = 'storagesets'
        ordering = ['StorageSetName']

    @staticmethod
    def storagesets():
        storagesets = []
        for b in StorageSets.objects.all():
            storagesets.append(b)
        return storagesets

    @staticmethod
    def delete_storageset(storagesetID):
        return StorageSets.objects.filter(pk=storagesetID).delete()

    @staticmethod
    def update_storageset(storagesetID, storageSet):
        StorageSets.objects.filter(pk=storagesetID).update(
            StorageSetName=storageSet["StorageSetName"],
            StoragePath=storageSet["StoragePath"],
            DevicePathID=storageSet["DevicePathID"])

    def __str__(self):
        return f'{self.StorageSetName}'


class FileSets(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    FileSetName = models.CharField(max_length=48, editable=True)
    Includes = models.CharField(max_length=256)
    Excludes = models.CharField(max_length=256)
    Compress = models.BooleanField(default=True)
    Recursive = models.BooleanField(default=False)
    EstimatedSize = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'filesets'
        ordering = ['FileSetName']

    @staticmethod
    def fileSets():
        fileSets = []
        for b in FileSets.objects.all():
            fileSets.append(b)
        return fileSets

    @staticmethod
    def includes():
        includes = []
        for b in FileSets.objects.all():
            includes.append(b.Includes)
        return includes

    @staticmethod
    def delete_fileset(filesetID):
        return FileSets.objects.filter(pk=filesetID).delete()

    @staticmethod
    def update_fileset(filesetID, fileSet):
        fileSet["Includes"] = str(fileSet["Includes"].replace("\n", ','))
        fileSet["Excludes"] = str(fileSet["Excludes"].replace("\n", ','))
        FileSets.objects.filter(pk=filesetID).update(
            FileSetName=fileSet["FileSetName"],
            Recursive=fileSet["Recursive"],
            Compress=fileSet["Compress"],
            Includes=fileSet["Includes"],
            Excludes=fileSet["Excludes"])

    @staticmethod
    def insert_fileset(fileSet):
        newFileSet = FileSets(
            FileSetName=fileSet["FileSetName"],
            Recursive=fileSet["Recursive"],
            Compress=fileSet["Compress"],
            Includes=fileSet["Includes"],
            Excludes=fileSet["Excludes"])
        try:
            newFileSet.save()
        except Exception as ie:
            return -1, ie

    def __str__(self):
        return f'{self.FileSetName}'


class Frequencies(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    Frequency = models.CharField(max_length=48)

    class Meta:
        db_table = 'frequencies'

    def __str__(self):
        return self.Frequency

    @staticmethod
    def frequencySets():
        frequencySets = []
        for b in Frequencies.objects.all():
            frequencySets.append(b)
        return frequencySets

    @staticmethod
    def load_frequencies():
        if len(Frequencies.objects.all()) == 0:
            for freq in "Daily", "Weekly", "Monthly", "Yearly", "Archive", "OnDemand":
                new_freq = Frequencies(
                    Frequency=freq)
                try:
                    new_freq.save()
                except Exception as ie:
                    return -1, ie


class DeviceTypes(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    DeviceType = models.CharField(max_length=24)

    class Meta:
        db_table = 'devicetypes'
        ordering = ['DeviceType']

    @staticmethod
    def deviceType():
        devices = []
        for d in DeviceTypes.objects.all():
            devices.append(d)
        return devices

    @staticmethod
    def load_devices():
        if len(DeviceTypes.objects.all()) == 0:
            for device in "DISK", "USB-Stick", "FILE", "CDROM", "EXTERNAL_DISK":
                new_device = DeviceTypes(
                    DeviceType=device)
                try:
                    new_device.save()
                except Exception as ie:
                    return -1, ie

    def __str__(self):
        return f'{self.DeviceType}'


class RootPaths(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    Root_Path = models.CharField(max_length=256)
    Max_Depth = models.SmallIntegerField(default=1)
    IsFolder = models.BooleanField(default=False)
    Active = models.BooleanField(default=False)

    class Meta:
        db_table = 'rootpaths'
        ordering = ['ID']

    @staticmethod
    def rootpaths():
        root_paths = []
        for rp in RootPaths.objects.all():
            root_paths.append(rp)
        return root_paths

    @staticmethod
    def delete_all_rootpaths():
        RootPaths.objects.all().delete()

    @staticmethod
    def reset_seq():
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER SEQUENCE public."rootpaths_ID_seq" RESTART 1')

    @staticmethod
    def insert_rootpath(rootpath):
        newRootPath = RootPaths(
            Root_Path=rootpath["Root_Path"],
            Max_Depth=rootpath["Max_Depth"],
            IsFolder=rootpath["IsFolder"],
            Active=rootpath["Active"]
        )
        try:
            newRootPath.save()
        except Exception as ie:
            return -1, ie

    @staticmethod
    def update_rootpath(rootpathID, rootpath):
        RootPaths.objects.filter(pk=rootpathID).update(
            Root_Path=rootpath["Root_Path"],
            Max_Depth=rootpath["Max_Depth"],
            IsFolder=rootpath["IsFolder"],
            Active=rootpath["Active"]
        )

    @staticmethod
    def load_rootpaths():
        choices = []
        partitions = psutil.disk_partitions()

        RootPaths.objects.all().delete()
        RootPaths.reset_seq()

        query_set = RootPaths.objects.values("Root_Path")
        for index in range(len(query_set)):
            for key in query_set[index]:
                choices.append((f'{index + 1}', f'{query_set[index][key]}'))

        for index in range(len(partitions)):
            act = False
            if partitions[index][1] not in choices and "snap" not in partitions[index][1]:
                if "DevApps" in f'{partitions[index][1]}':
                    act = True
                    new_rootpath = RootPaths(
                        Root_Path=f'{partitions[index][1]}',
                        Max_Depth=1,
                        IsFolder=True,
                        Active=act)
                    try:
                        new_rootpath.save()
                    except Exception as ie:
                        return -1, ie

    @staticmethod
    def rpChoices():
        choices = []
        query_set = RootPaths.objects.values("Root_Path")
        for index in range(len(query_set)):
            for key in query_set[index]:
                choices.append((f'{index + 1}', f'{query_set[index][key]}'))
        return choices

    @staticmethod
    def active_choice():
        achoice = []
        query_set = RootPaths.objects.filter(Active=1)
        if len(query_set) > 0:
            for index in range(len(query_set)):
                achoice.append(f'{query_set[index]}')
            return achoice[0]
        else:
            return ""

    @staticmethod
    def selectRootPath(rootpath_id, rootpathSet):
        RootPaths.objects.all().update(Active=False)
        RootPaths.objects.filter(pk=rootpath_id).update(Active=True)

    def __str__(self):
        return f'{self.Root_Path}'


class LoggingLevels(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    LogLevel = models.CharField(max_length=12)
    Active = models.BooleanField(default=False)

    class Meta:
        db_table = 'logginglevels'
        ordering = ['ID']

    @staticmethod
    def logLevels():
        levels = []
        for ol in LoggingLevels.objects.all():
            levels.append(ol)
        return levels

    @staticmethod
    def llChoices():
        choices = []
        query_set = LoggingLevels.objects.values("LogLevel")
        for index in range(len(query_set)):
            for key in query_set[index]:
                choices.append((f'{index + 1}', f'{query_set[index][key]}'))
        return choices

    @staticmethod
    def active_choice():
        achoice = []
        query_set = LoggingLevels.objects.filter(Active=1)
        if len(query_set) > 0:
            for index in range(len(query_set)):
                achoice.append(f'{query_set[index]}')
            return achoice[0]
        else:
            return ""

    @staticmethod
    def load_levels():
        if len(LoggingLevels.objects.all()) == 0:
            for lvl in "CRITICAL", "ERROR", "WARN", "INFO", "DEBUG":
                act = False
                if lvl == "WARN":
                    act = True
                new_level = LoggingLevels(
                    LogLevel=lvl,
                    Active=act)
                try:
                    new_level.save()
                except Exception as ie:
                    return -1, ie

    @staticmethod
    def update_loglevel(loglevel_id):
        LoggingLevels.objects.all().update(Active=False)
        LoggingLevels.objects.filter(pk=loglevel_id).update(Active=True)

    def __str__(self):
        return f'{self.LogLevel}'


class BaseFileSets(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    FileSetName = models.CharField(max_length=48)
    Includes = models.CharField(max_length=256)
    Excludes = models.CharField(max_length=256)
    Compress = models.BooleanField(default=True)
    Recursive = models.BooleanField(default=False)
    EstimatedSize = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'basefilesets'
        ordering = ['Includes']

    def __str__(self):
        return f'{self.FileSetName}'

    @staticmethod
    def basefileSets():
        basefileSets = []
        for f in BaseFileSets.objects.all():
            basefileSets.append(f)
        return basefileSets

    @staticmethod
    def includes():
        includes = []
        for b in BaseFileSets.objects.all():
            includes.append(b.Includes)
        return includes

    @staticmethod
    def delete_basefileset(filesetID):
        return BaseFileSets.objects.filter(pk=filesetID).delete()

    @staticmethod
    def update_basefileset(filesetID, fileSet):
        fileSet["Includes"] = str(fileSet["Includes"].replace("\n", ','))
        fileSet["Excludes"] = str(fileSet["Excludes"].replace("\n", ','))
        BaseFileSets.objects.filter(pk=filesetID).update(
            FileSetName=fileSet["FileSetName"],
            Recursive=fileSet["Recursive"],
            Compress=fileSet["Compress"],
            Includes=fileSet["Includes"],
            Excludes=fileSet["Excludes"])


class BackupSets(models.Model):
    objects = None

    ID = models.AutoField(primary_key=True)
    BackupSetName = models.CharField(max_length=48)
    StorageSetID = models.ForeignKey('storagesets', on_delete=models.CASCADE)
    FileSetName = models.CharField(max_length=48)
    FrequencyID = models.ForeignKey('frequencies', on_delete=models.CASCADE)
    Versions = models.IntegerField(default=1)
    EstimatedSize = models.BigIntegerField

    class Meta:
        db_table = 'backupsets'
        ordering = ['BackupSetName']

    def __str__(self):
        return self.BackupSetName

    @staticmethod
    def backupsets():
        backupsets = []
        for b in BackupSets.objects.all():
            backupsets.append(b)
        return backupsets

    @staticmethod
    def show_backupset(backupSetID):
        return BackupSets.objects.filter(pk=backupSetID)

    @staticmethod
    def delete_backupset(backupSetID):
        return BackupSets.objects.filter(pk=backupSetID).delete()

    @staticmethod
    def update_backupset(backupSetID, update_set):
        bkquery_set = BackupSets.objects.filter(pk=backupSetID)

        rc = bkquery_set.update(BackupSetName=update_set["BackupSetName"],
                                FileSetName=update_set["FileSetName"],
                                StorageSetID=update_set["StorageSetID"],
                                FrequencyID=update_set["FrequencyID"],
                                Versions=update_set["Versions"])
        return rc
