from django.db import models


class StorageSets(models.Model):
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

    def __str__(self):
        return f'{self.Frequency}'


class DeviceTypes(models.Model):
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

    def __str__(self):
        return f'{self.DeviceType}'


class LogLevel(models.Model):
    ID = models.AutoField(primary_key=True)
    Loglevel = models.CharField(max_length=12,
                                name="Loglevel")
    Active = models.BooleanField(default=False)

    class Meta:
        db_table = 'loglevel'
        ordering = ['ID']

    @staticmethod
    def logLevel():
        levels = []
        for ol in LogLevel.objects.all():
            levels.append(ol)
        return levels

    @staticmethod
    def llChoices():
        choices = []
        query_set = LogLevel.objects.values('Loglevel')
        for index in range(len(query_set)):
            for key in query_set[index]:
                choices.append((f'{index + 1}', f'{query_set[index][key]}'))
        return choices

    @staticmethod
    def active_choice():
        achoice = []
        query_set = LogLevel.objects.filter(Active=1)
        for index in range(len(query_set)):
            achoice.append(f'{query_set[index]}')
        return achoice[0]

    @staticmethod
    def update_loglevel(loglevel_id):
        LogLevel.objects.all().update(Active=False)
        LogLevel.objects.filter(pk=loglevel_id).update(
            Active=True)

    def __str__(self):
        return f'{self.Loglevel}'


class BaseFileSets(models.Model):
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
