from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def requests_retry_session(session, retries=3, backoff_factor=0.3, status_forcelist=(404, 500, 502, 503, 504)):
    retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
