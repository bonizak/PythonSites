from pathlib import Path

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader

from .forms import RootPathsForm, LogLevelForm
from .models import BackupSets, Frequencies, StorageSets, FileSets, BaseFileSets, DeviceTypes, RootPaths, LoggingLevels


def testindex(request):
    # return HttpResponse("Hello, world. You're at the Backup GUI index.")

    BASE_DIR = Path(__file__).resolve().parent.parent
    template = loader.get_template('backupgui/testindex.html')
    context = {'index': "index", 'basedir': BASE_DIR}
    return HttpResponse(template.render(context, request))


def index(request):
    BASE_DIR = Path(__file__).resolve().parent.parent
    template = loader.get_template('backupgui/index.html')
    context = {'index': "index", 'basedir': BASE_DIR}
    return HttpResponse(template.render(context, request))


# ==========================================================
# Index Pages
def backupsets(request):
    backupsets_list = BackupSets.backupsets()
    template = loader.get_template('backupgui/backupsets.html')
    context = {'backupsets_list': backupsets_list}
    return HttpResponse(template.render(context, request))


def file_storag_sets(request):
    filesets_list = FileSets.fileSets()
    storagesets_list = StorageSets.storagesets()
    template = loader.get_template('backupgui/file_storag_sets.html')
    context = {'storagesets_list': storagesets_list,
               'filesets_list': filesets_list}
    return HttpResponse(template.render(context, request))


def basefilesets(request):
    append_set = []
    basefilesets = BaseFileSets.basefileSets()
    filesets_includes = FileSets.includes()
    basefileset_includes = BaseFileSets.includes()
    basefileset_diffs = list(set(basefileset_includes) - set(filesets_includes))

    for basefileset in basefilesets:
        for basefileset_diff in basefileset_diffs:
            if basefileset.Includes == basefileset_diff:
                append_set.append(basefileset)
    template = loader.get_template('backupgui/basefilesets.html')
    context = {'basefilesets_list': append_set}
    return HttpResponse(template.render(context, request))


# ==========================================================
# BACK UP Set Views
def singleBackupSet(request, backupset_id):
    fileset_options = FileSets.objects.distinct('FileSetName')
    storageset_options = StorageSets.objects.all()
    query_set = get_object_or_404(BackupSets, pk=backupset_id)
    context = {'singlebackupset': query_set,
               'ssoptions': storageset_options,
               'fsoptions': fileset_options,
               'freqoptions': Frequencies.objects.all()}
    return render(request, 'backupgui/edit_backupset.html', context)


def updateBackupSet(request, backupset_id):
    update_set = {}
    delete_set = {}
    if 'cancel' in request.POST:
        context = {'emptySet': "Backup Set Update Cancelled"}
        return render(request, 'backupgui/results.html', context)
    elif 'delete' in request.POST:
        delete_set["ID"] = backupset_id
        rc = BackupSets.delete_backupset(backupset_id)
        context = {'delete_set': "BackupSet",
                   'delete_msg': f"Backup Set {request.POST['backupsetname']} Deleted! "}
        return render(request, 'backupgui/results.html', context)
    else:
        update_set["ID"] = backupset_id
        update_set["BackupSetName"] = request.POST['backupsetname']
        update_set["FileSetName"] = request.POST['filesetname']
        update_set["StorageSetID"] = request.POST['storagesetname']
        update_set["FrequencyID"] = request.POST['frequencies']
        update_set["Versions"] = request.POST['versions']
        rc = BackupSets.update_backupset(backupset_id, update_set)

        print(f"Return from update {rc}")
        context = {'backupset': update_set, 'return_code': rc}
        return render(request, 'backupgui/results.html', context)


# ==========================================================
# File Set Views
def singleFileset(request, fileset_id):
    query_set = get_object_or_404(FileSets, pk=fileset_id)
    query_set.Includes = str(query_set.Includes).replace(",", "\n")
    query_set.Excludes = str(query_set.Excludes).replace(",", "\n")
    query_set.EstimatedSize = f'{query_set.EstimatedSize:.2f}'
    template = loader.get_template('backupgui/edit_fileset.html')
    context = {'singlefileset': query_set}
    return render(request, 'backupgui/edit_fileset.html', context)


def updateFileSet(request, fileset_id):
    fupdate_set = {}
    delete_set = {}
    if 'cancel' in request.POST:
        context = {'emptySet': "File Set Update Cancelled"}
        return render(request, 'backupgui/results.html', context)
    elif 'delete' in request.POST:
        delete_set["ID"] = fileset_id
        rc = FileSets.delete_fileset(fileset_id)
        context = {'delete_set': "FileSet",
                   'delete_msg': f"File Set {request.POST['filesetname']} Deleted! "}
        return render(request, 'backupgui/results.html', context)
    else:
        fupdate_set["ID"] = fileset_id
        fupdate_set["FileSetName"] = request.POST['filesetname']
        fupdate_set["Includes"] = request.POST['includes']
        fupdate_set["Excludes"] = request.POST['excludes']
        fupdate_set["Recursive"] = request.POST['recursive']
        fupdate_set["Compress"] = request.POST['compress']
        rc = FileSets.update_fileset(fileset_id, fupdate_set)

        print(f"Return from update {rc}")
        context = {'fupdate_set': fupdate_set, 'return_code': rc}
        return render(request, 'backupgui/results.html', context)


# ==========================================================
# Storage Set Views
def singleStorageset(request, storageset_id):
    devicetype_options = DeviceTypes.objects.all()
    query_set = get_object_or_404(StorageSets, pk=storageset_id)
    template = loader.get_template('backupgui/edit_storageset.html')
    context = {'singlestorageset': query_set,
               'dt_options': devicetype_options}
    return render(request, 'backupgui/edit_storageset.html', context)


def updateStorageSet(request, storageset_id):
    supdate_set = {}
    delete_set = {}
    if 'cancel' in request.POST:
        context = {'emptySet': "Storage Set Update Cancelled"}
        return render(request, 'backupgui/results.html', context)
    elif 'delete' in request.POST:
        delete_set["ID"] = storageset_id
        rc = StorageSets.delete_storageset(storageset_id)
        context = {'delete_set': "StorageSet",
                   'delete_msg': f"Storage Set {request.POST['storagesetname']} Deleted! "}
        return render(request, 'backupgui/results.html', context)
    else:
        supdate_set["ID"] = storageset_id
        supdate_set["StorageSetName"] = request.POST['storagesetname']
        supdate_set["StoragePath"] = request.POST['storagepath']
        supdate_set["DevicePathID"] = request.POST['devicepathtype']
        rc = StorageSets.update_storageset(storageset_id, supdate_set)

        print(f"Return from update {rc}")
        context = {'supdate_set': supdate_set, 'return_code': rc}
        return render(request, 'backupgui/results.html', context)


# ==========================================================
# Base File Set Views
def singleBaseFileset(request, fileset_id):
    query_set = get_object_or_404(BaseFileSets, pk=fileset_id)
    query_set.Includes = str(query_set.Includes).replace(",", "\n")
    query_set.Excludes = str(query_set.Excludes).replace(",", "\n")
    template = loader.get_template('backupgui/edit_basefileset.html')
    context = {'singleBaseFileset': query_set}
    return render(request, 'backupgui/edit_basefileset.html', context)


def updateBaseFileset(request, fileset_id):
    bfupdate_set = {}
    delete_set = {}
    if 'cancel' in request.POST:
        context = {'emptySet': "Base File Set Update Cancelled"}
        return render(request, 'backupgui/results.html', context)
    elif 'delete' in request.POST:
        delete_set["ID"] = fileset_id
        rc = BaseFileSets.delete_basefileset(fileset_id)
        context = {'delete_set': "BaseFileSet",
                   'delete_msg': f"Base File Set {request.POST['filesetname']} Deleted! "}
        return render(request, 'backupgui/results.html', context)
    else:
        bfupdate_set["ID"] = fileset_id
        bfupdate_set["FileSetName"] = request.POST['filesetname']
        bfupdate_set["Includes"] = request.POST['includes']
        bfupdate_set["Excludes"] = request.POST['excludes']
        bfupdate_set["Recursive"] = request.POST['recursive']
        bfupdate_set["Compress"] = request.POST['compress']
        rc = BaseFileSets.update_basefileset(fileset_id, bfupdate_set)

        print(f"Return from update {rc}")
        context = {'bfupdate_set': bfupdate_set, 'return_code': rc}
        return render(request, 'backupgui/results.html', context)


def addBaseFileset(request):
    added_basefileset = {}
    added_basefilesets = []
    added_includes = []
    context = {}
    if request.method == 'POST':
        checked_fileset_IDs = request.POST.getlist('bfiselect')
        for checked_fileset_id in checked_fileset_IDs:
            checked_basefileset = get_object_or_404(BaseFileSets, pk=checked_fileset_id)
            checked_include = checked_basefileset.Includes

            if FileSets.includes().__contains__(checked_include):
                print(f'Includes {checked_include} already exists in FileSets')
            else:
                added_basefileset["FileSetName"] = checked_basefileset.FileSetName
                added_basefileset["Includes"] = checked_basefileset.Includes
                added_basefileset["Excludes"] = checked_basefileset.Excludes
                added_basefileset["Compress"] = checked_basefileset.Compress
                added_basefileset["Recursive"] = checked_basefileset.Recursive
            rc = FileSets.insert_fileset(added_basefileset)

            if rc == -1:
                added_basefilesets.append(f'Failed to add {checked_basefileset.Includes}')
            else:
                added_basefilesets.append(f'Added {checked_basefileset.Includes}')

        context = {'added_basefilesets': added_basefilesets}

        return render(request, 'backupgui/results.html', context)


def utilities(request):
    LoggingLevels.load_levels()
    DeviceTypes.load_devices()
    Frequencies.load_frequencies()
    ll_choice = LoggingLevels.active_choice()
    loglevel_form = LogLevelForm()
    device_list = DeviceTypes.deviceType()
    frequency_list = Frequencies.frequencySets()
    template = loader.get_template('backupgui/utilities.html')
    context = {'frequency_list': frequency_list,
               'device_list': device_list,
               'loglevel_form': loglevel_form,
               'll_choice': ll_choice
               }

    return HttpResponse(template.render(context, request))


def updateLogLevel(request):
    query_set = get_object_or_404(LoggingLevels, pk=request.POST["LOGLEVEL_CHOICES"])
    LoggingLevels.update_loglevel(request.POST["LOGLEVEL_CHOICES"])
    context = {'updated_loglevel': query_set}
    return render(request, 'backupgui/results.html', context)


def rootpaths(request):
    RootPaths.load_rootpaths()
    rp_choice = RootPaths.active_choice()
    rootpath_form = RootPathsForm()
    template = loader.get_template('backupgui/rootpaths.html')
    context = {'rootpath_form': rootpath_form,
               'rp_choice': rp_choice}
    return HttpResponse(template.render(context, request))


def updateRootPath(request, rootpath_id):
    update_set = {}
    if 'cancel' in request.POST:
        context = {'emptySet': "Root Path Update Cancelled"}
        return render(request, 'backupgui/results.html', context)
    else:
        update_set["ID"] = rootpath_id
        update_set["Root_Path"] = request.POST['Root_Path']
        update_set["Max_Depth"] = request.POST['Max_Depth']
        update_set["IsFolder"] = request.POST[True]
        update_set["Active"] = request.POST[True]
        rc = RootPaths.update_rootpath(rootpath_id, update_set)

        print(f"Return from update {rc}")
        context = {'rootpathset': update_set, 'return_code': rc}
        return render(request, 'backupgui/results.html', context)
