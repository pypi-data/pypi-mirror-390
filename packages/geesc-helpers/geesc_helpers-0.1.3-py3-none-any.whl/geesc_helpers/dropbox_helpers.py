from os import getenv
from hashlib import sha256
from contextlib import closing
from dotenv import find_dotenv, load_dotenv, set_key
from dropbox import DropboxOAuth2FlowNoRedirect, Dropbox, exceptions
from io import BytesIO

DROPBOX_HASH_CHUNK_SIZE = 4*1024*1024

def compute_local_hash(file_bytes):
    block_hashes = b''
    while True:
        chunk = file_bytes.read(DROPBOX_HASH_CHUNK_SIZE)
        if not chunk:
            break
        block_hashes += sha256(chunk).digest()
    return sha256(block_hashes).hexdigest()

def auth(path = None):
    if path is not None:
        dotenv_file = find_dotenv(path)
        load_dotenv(dotenv_file)
    else:
        dotenv_file = find_dotenv()
        load_dotenv(dotenv_file)

    APP_KEY = getenv('APP_KEY')
    APP_SECRET = getenv('APP_SECRET')

    # Confere se precisa fazer o refresh token:
    if getenv("REFRESH_TOKEN") is None:
        auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET,locale="pt_br", token_access_type='offline')
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        try:
            oauth_result = auth_flow.finish(auth_code)
            set_key(dotenv_file, "REFRESH_TOKEN", oauth_result.refresh_token)
            REFRESH_TOKEN = oauth_result.refresh_token
        except Exception as e:
            print('Error: %s' % (e,))
            exit(1)
    else:
        REFRESH_TOKEN = getenv('REFRESH_TOKEN')

    dbx = Dropbox(app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=REFRESH_TOKEN)
    return dbx


def download_dropbox(dbx, path):
    try:
        _, res = dbx.files_download(path)
        with closing(res) as result:
            data = bytearray(res.content)
        return data
    except exceptions.HttpError as err:
        print('*** HTTP error:', err)
        return None

def get_hash(dbx, path):
    try:
        _, res = dbx.files_download(path)
        with closing(res) as result:
            data = bytearray(res.content)
        return data
    except exceptions.HttpError as err:
        print('*** HTTP error:', err)
        return None

def try_download(dbx, dropbox_path, local_path):
    try:
        # Confere o arquivo local
        with open(local_path, "rb") as f:
            hash_local = compute_local_hash(f)
            dropbox_hash = dbx.files_get_metadata(dropbox_path).content_hash
        # se for diferente o hash, baixa de novo do dropbox
        if hash_local != dropbox_hash:
            print(f"Local file is not up to date, downloading from dropbox: {dropbox_path}")
            new_file = BytesIO(download_dropbox(dbx, dropbox_path))
            with open(local_path, "wb") as f:
                f.write(new_file.getbuffer())
            return new_file
        # se for igual lê o local mesmo e passa os bytes pra função de fora
        elif hash_local == dropbox_hash:
            print(f"Local file up to date, reading local: {local_path}")
            with open(local_path, "rb") as f:
                return BytesIO(f.read())
    # Se o arquivo n existe, pega do dropbox
    except FileNotFoundError:
        print(f"File not Found, downloading from dropbox: {dropbox_path}")
        new_file = BytesIO(download_dropbox(dbx, dropbox_path))
        with open(local_path, "wb") as f:
            f.write(new_file.getbuffer())
        return new_file
    except Exception as e:
        print(f"Erro: {e}")
        return None