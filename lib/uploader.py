'''
simple SFTP data uploader
'''
from lib.utils import *
from pathlib import Path

CACHE_NAME = 'uploads.json'

class Uploader:

    def __init__(self, data_dir: str, remote_dir: str):
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        self.data_dir = data_dir
        self.remote_dir = remote_dir
        self.cache = self.init_upload_cache()
        log_debug("Uploader intialized")


    def upload(self) -> bool:
        '''
        uploads all files in the data_dir directory that have not been uploaded yet
        :return: True if all files were uploaded, False otherwise
        '''

        # if all files were uploaded
        result = True

        files = os.listdir(self.data_dir)
        files.remove(CACHE_NAME)

        client = get_server_conn()
        sftp = client.open_sftp()

        for file in files:
            if file not in self.cache['uploads']:
                try:
                    local_path = f"{self.data_dir}/{file}"
                    remote_path = f"{self.remote_dir}/{file}"
                    log(f"Beginning transfer of {local_path} to server:{remote_path}")
                    sftp.put(local_path, remote_path)
                    self.cache['uploads'][file] = {'upload-time': get_string_time_now()}
                    log(f"File {local_path} transferred to {remote_path}")
                except Exception as e:
                    # we treat this as non-fatal and retry later
                    # when coming back to upload state
                    log_warn(f"error transferring file {file}: {e}")
                    result = False
                    continue

        client.close()

        with open(f'{self.data_dir}/{CACHE_NAME}', 'w') as f:
            json.dump(self.cache, f)

        return result
        

    def init_upload_cache(self):   
        '''
        initializes the upload cache
        '''
        if not os.path.exists(f'{self.data_dir}/{CACHE_NAME}'):
            with open(f'{self.data_dir}/{CACHE_NAME}', 'w') as f:
                dummy = {"uploads": {}}
                json.dump(dummy, f)
            return dummy
        else:
            with open(f'{self.data_dir}/{CACHE_NAME}', 'r') as f:
                return json.load(f)
            
