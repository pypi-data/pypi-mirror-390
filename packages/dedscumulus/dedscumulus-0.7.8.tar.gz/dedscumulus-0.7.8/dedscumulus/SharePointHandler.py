from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.builder import ODataPathBuilder
import tempfile
import os
import time
import shutil


class SharePointHandler:
    """ Handler for file operations on SharePoint.
    """

    def __init__(self, CREDS, site_url, base_dir, logger):
        logger.debug(f"Initializing SharePointHandler with site_url {site_url}")
        self.site_url = site_url
        self.base_dir = base_dir
        self.username = CREDS['sp_user']
        self.password = CREDS['sp_password']

        # Setup SP-Logger
        self.logger = logger

        # Initialize SharePoint client context
        self.ctx = (ClientContext(self.site_url)
            .with_credentials(
            UserCredential(self.username, self.password)))

        # Create temporary directory
        self.tempdir = tempfile.TemporaryDirectory()

    def __del__(self):
        """Delete temporary directory at deconstruction"""
        self.tempdir.cleanup()

    def ctx(self):
        return self.ctx

    def reset_ctx(self):
        """ Reset client context"""
        self.ctx = (ClientContext(self.site_url)
            .with_credentials(
            UserCredential(self.username, self.password)))

    def get_tempdir(self):
        """Provide temporary directory for other functions to use"""
        return self.tempdir.name

    def list_folders(self, folderpath, absolute_path=False) -> [Folder]:
        try:
            self.logger.debug(f"Starting list_folders")
            """ List all folders in a directory """
            if absolute_path:
                folder_url = folderpath
            else:
                folder_url = self.base_dir + folderpath
            self.logger.debug(f"Folder URL: {folder_url}")
            folder_query = self.ctx.web.get_folder_by_server_relative_url(folder_url)
            self.logger.debug(f"Folder queried")
            folder_query.expand(["Folders"]).get().execute_query_retry(max_retry=1)
            self.logger.debug(f"Folder expaned")
            self.ctx.execute_query()
            self.logger.debug(f"CTX queried")
            folder_count=len(folder_query.folders)
            self.logger.debug(f"Found {folder_count} subfolders under {folder_url}")
            return folder_query.folders
        except Exception as e:
            self.logger.error("list_folders error: "+str(e))
            return None

    def list_files(self, folderpath, absolute_path=False) -> [File]:
        try:
            """ List all files in a directory"""
            if absolute_path:
                folder_url = folderpath
            else:
                folder_url = self.base_dir + folderpath
            folder_query = self.ctx.web.get_folder_by_server_relative_url(folder_url)
            folder_query.expand(["Files"]).get().execute_query_retry(max_retry=1)
            self.ctx.execute_query()
            file_count=len(folder_query.files)
            self.logger.debug(f"Found {file_count} files in {folder_url}")
            return folder_query.files
        except Exception as e:
            self.logger.error("list_files error: "+str(e))
            return None

    def folder_exists(self, folderpath, absolute_path=False):
        """ Checks if a given folder exists and returns Boolean value """
        try:
            if absolute_path:
                folder_url = folderpath
            else:
                folder_url = self.base_dir + folderpath
            folder = (self.ctx.web.get_folder_by_server_relative_url(folder_url).select("Exists").get().execute_query_retry(max_retry=1))
            return folder.exists
        except Exception as e:
            self.logger.error("folder_exists error: "+str(e))
            return None

    def file_exists(self, filepath, absolute_path=False):
        """ Checks if a given file exists and returns Boolean value """
        if absolute_path:
            file_url = filepath
        else:
            file_url = self.base_dir + filepath
        try:
            file = self.ctx.web.get_folder_by_server_relative_url(file_url).get().execute_query()
            return True
        except ClientRequestException as e:
            if e.response.status_code == 404:
                return False
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            else:
                raise ValueError(e.response.text)

    def folder_empty(self, folderpath, absolute_path=False):
        """ Checks if a folder is empty"""
        folderlist = self.list_folders(folderpath, absolute_path)
        filelist = self.list_files(folderpath, absolute_path)
        if len(filelist) == 0 and len(folderlist) == 0:
            return True
        else:
            return False

    def makedirs(self, folderpath, absolute_path=False):
        """ Creates directory and subdirectories recursively
            Only accesses base dir, due to restricted credentials.
            Unfortunately this breaks the use of ctx.web.ensure_folder_path()
        """
        if absolute_path:
            # Remove base dir from folderpath
            folder_url = folderpath.replace(self.base_dir, '/')
        else:
            folder_url = folderpath
        try:
            url_component = os.path.normpath(folder_url).split(os.path.sep)
            url_component = [part for part in url_component if part]
            if not url_component:
                raise NotADirectoryError("Wrong relative URL provided")
            child_folder = self.ctx.web.get_folder_by_server_relative_url(self.base_dir).get()
            for url_part in url_component:
                child_folder = child_folder.add(url_part).execute_query_retry(max_retry=3)
            return child_folder
        except ClientRequestException as e:
            self.logger.error(f'Failed to create directories with path {folder_url}')
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            self.reset_ctx()
            raise e

    def rmdir(self, folderpath, absolute_path=False):
        """ Deletes folder """
        if absolute_path:
            folder_url = folderpath
        else:
            folder_url = self.base_dir + folderpath
        try:
            self.ctx.web.get_folder_by_server_relative_url(folder_url).delete_object().execute_query_retry(max_retry=3)
        except ClientRequestException as e:
            self.logger.error(f'Failed to delete folder {folder_url}')
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            raise e

    def delete_file(self, filepath, absolute_path=False):
        """ Deletes file """
        if absolute_path:
            file_url = filepath
        else:
            file_url = self.base_dir + filepath
        try:
            self.ctx.web.get_file_by_server_relative_url(file_url).delete_object().execute_query_retry(max_retry=3)
        except ClientRequestException as e:
            self.logger.error(f'Failed to delete file {file_url}')
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            raise e

    def manual_move(self, url_old, url_new):
        """ Moves a file using download, upload and delete operations instead
            of built-in move function. Probably slower than built-in, but fixes
            URL length limit problem.
        """
        # Download source file
        source_file = self.download(url_old, True)
        # Manually rename local file
        local_file_new_name = os.path.join(os.path.dirname(source_file), os.path.basename(url_new))
        shutil.move(source_file, local_file_new_name)
        self.upload(local_file_new_name, os.path.dirname(url_new), True)
        self.delete_file(url_old, True)

    def move(self, path_old, path_new, absolute_path=False):
        """ Move a file """
        if absolute_path:
            url_old = path_old
            url_new = path_new
        else:
            url_old = self.base_dir + path_old
            url_new = self.base_dir + path_new

        # There's a known limitation to the URL length for the move operation.
        # If the URL length exceeds 260, the built-in move-method does not work
        # and a workaround needs to be used.
        #
        # See following links concerning this problem:
        # https://sharepoint.stackexchange.com/questions/243518/400-errors-moving-files-by-rest-api-long-url
        # https://github.com/vgrem/Office365-REST-Python-Client/issues/319
        try:
            # Built-in method:
            if (len(self.site_url) + len(url_old) + len(url_new)) < 256:
                source_file = self.ctx.web.get_file_by_server_relative_url(url_old)
                source_file.moveto(url_new, 1)  # 1: overwrites a file with same name if exists
                self.ctx.execute_query_retry()

            # Workaround from user @dvinesett
            # See https://github.com/vgrem/Office365-REST-Python-Client/issues/319
            else:
                file = self.ctx.web.get_file_by_server_relative_url(url_old).get().execute_query()
                file_id = file.unique_id

                get_file_query_string = "getFileById('{}')".format(file_id)

                moveto_query_params = {'newurl': url_new, 'flags': 1}
                #moveto_query_string = ODataUrlBuilder.build('moveto', moveto_query_params)
                moveto_query_string = ODataPathBuilder.build('moveto', moveto_query_params)

                moveto_url = '/'.join([self.ctx.service_root_url(), 'web', get_file_query_string, moveto_query_string])
                request = RequestOptions(moveto_url)
                request.method = 'POST'
                self.ctx.ensure_form_digest(request)
                for retry in range(0, 3):
                    try:
                        res = self.ctx.pending_request().execute_request_direct(request)
                        if res.status_code != 200:
                            raise ClientRequestException(response=res)
                        break
                    except Exception as e:
                        time.sleep(5)
        except ClientRequestException as e:
            self.logger.debug('Failed to move file using built-in method.'
                             'Attempting manual move operation.')
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            try:
                self.manual_move(url_old, url_new)
            except ClientRequestException as e:
                self.logger.error(f'Failed to move file on SharePoint '
                                  f'with old file URL:\n {url_old}'
                                  f'to new file URL:\n {url_new}')
                self.reset_ctx()
                raise e

    def download(self, filepath, absolute_path=False) -> str:
        """ Downloads a file to a temporary directory and returns temporary path."""
        if absolute_path:
            file_url = filepath
        else:
            file_url = self.base_dir + filepath

        download_path = os.path.join(self.tempdir.name, os.path.basename(file_url))
        with open(download_path, "wb") as local_file:
            try:
                (self.ctx.web.get_file_by_server_relative_path(file_url)
                 .download(local_file).execute_query_retry(max_retry=3))
            except ClientRequestException as e:
                self.logger.error(f'Server Errror: Failed to download file from'
                                  f' SharePoint with file URL:\n {file_url}')
                if e.response.status_code == 429:
                    # Automatically wait, if there is 'Too many requests' error
                    time.sleep(e.response.header['Retry-After'])
                self.reset_ctx()
                raise e
            except ValueError as e:
                self.logger.error(f'Write Error: Failed to write local file. File URL: {file_url}')
                raise e
        return download_path

    def upload(self, filepath, folder_path, absolute_path=False):
        """ Uploads a file to given url """
        if absolute_path:
            folder_url = folder_path
        else:
            folder_url = self.base_dir + folder_path

        with open(filepath, 'rb') as content_file:
            file_content = content_file.read()

        target_folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        name = os.path.basename(filepath)
        try:
            target_file = target_folder.upload_file(name, file_content).execute_query_retry(max_retry=3)
        except ClientRequestException as e:
            self.logger.error(f'Failed to upload file to SharePoint with file URL: {folder_url}/{name}')
            if e.response.status_code == 429:
                # Automatically wait, if there is 'Too many requests' error
                time.sleep(e.response.header['Retry-After'])
            self.reset_ctx()
            raise e
