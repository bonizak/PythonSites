from django.urls import path, re_path
from . import views

app_name = 'backupgui'
urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('abasefilesets', views.addBaseFileset, name='addBaseFileset'),
    path('basefilesets', views.basefilesets, name='basefilesets'),
    path('backupsets', views.backupsets, name='backupsets'),
    path('file_storag_sets', views.file_storag_sets, name='file_storag_sets'),
    path('rootpaths', views.rootpaths, name='rootpaths'),
    path('updateRootPath/<int:rootpath_id>', views.updateRootPath, name='updateRootPath'),
    path('sibasefilesets/<int:fileset_id>', views.singleBaseFileset, name='singleBaseFileset'),
    path('sibackupsets/<int:backupset_id>', views.singleBackupSet, name='singleBackupSet'),
    path('sifiset/<int:fileset_id>', views.singleFileset, name='singleFileset'),
    path('sisset/<int:storageset_id>', views.singleStorageset, name='singleStorageset'),
    path('updbasefilesets/<int:fileset_id>', views.updateBaseFileset, name='updateBaseFileset'),
    path('updbackupsets/<int:backupset_id>', views.updateBackupSet, name='updateBackupSet'),
    path('updfiset/<int:fileset_id>', views.updateFileSet, name='updateFileSet'),
    path('updateLogLevel', views.updateLogLevel, name='updateLogLevel'),
    path('updsset/<int:storageset_id>', views.updateStorageSet, name='updateStorageSet'),
    path('utilities', views.utilities, name='utilities'),
    path('testindex', views.testindex, name='testindex'),
]
