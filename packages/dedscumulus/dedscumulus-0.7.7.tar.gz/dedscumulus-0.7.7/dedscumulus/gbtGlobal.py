from greenbyteapi.greenbyteapi_client import GreenbyteapiClient
#from greenbyteapi.configuration import Configuration
#from greenbyteapi.models.status_item import StatusItem

def createClient(CREDS,LOGGER):
    try:
        greenbyte_client = GreenbyteapiClient()
        greenbyte_client.config.x_api_key=CREDS['brz_token']
        greenbyte_client.config.customer=CREDS['brzConfig']
        #still not supported
        #greenbyte_client.config.timeout=120
        #greenbyte_client.config.max_retries=3
        return greenbyte_client
    except Exception as ge:
        LOGGER.error(f"ERROR: Could not initalize greenbyte_client: "+str(ge))
        return None

def getData(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getData with parameters {QUERY_PARAMS}")
            return greenbyte_client.data.get_data(QUERY_PARAMS['deviceIds'],QUERY_PARAMS['dataSignalIds'],QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampEnd'],False,QUERY_PARAMS['resolution'],'device',0,None)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_data from Breeze not received, try {tries}, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: get_data from Breeze timed out for devices: {QUERY_PARAMS['deviceIds']}. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: get_data from Breeze not received, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
                return None
            
def getStatuses(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running gbtGlobal.getStatuses with parameters {QUERY_PARAMS}")
            response = greenbyte_client.statuses.get_statuses(QUERY_PARAMS['deviceIds'],QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampFinish'],QUERY_PARAMS['categories'],
                                                          QUERY_PARAMS['lostProductionSignalId'],None,None,False,QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'],False,'custom')
            if type(response) is list:
                return response
            else:
                LOGGER.error(f"ERROR: gbtGlobal.getStatuses from Breeze returned a non-list response. Check parameters of the greenbyte_client.")
                return None
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_statuses from Breeze not received, try {tries}, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: gbtGlobal.getStatuses from Breeze timed out for devices: {QUERY_PARAMS['deviceIds']}. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: gbtGlobal.getStatuses from Breeze not received, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
                return None
            
def getSiteAccesses(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getAccesses with parameters {QUERY_PARAMS}")
            return greenbyte_client.plan.list_site_accesses(QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampFinish'],QUERY_PARAMS['deviceIds'],QUERY_PARAMS['siteIds'],
                                                          QUERY_PARAMS['fields'],QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'],QUERY_PARAMS['useUtc'])
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: list_site_accesses from Breeze not received, try {tries}, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: list_site_accesses from Breeze timed out for devices: {QUERY_PARAMS['deviceIds']}. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: list_site_accesses from Breeze not received, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
                return None
            
def getSites(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getSites with parameters {QUERY_PARAMS}")
            return greenbyte_client.assets.get_sites('siteId,metadata,title,country',QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'])
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_sites from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: get_sites from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: get_sites from Breeze not received, error: "+str(ge))
                return None
            
def getDevices(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getDevices with parameters {QUERY_PARAMS}")
            return greenbyte_client.assets.get_devices(QUERY_PARAMS['device_type_ids'],None,None,QUERY_PARAMS['fields'],QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'],False)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_devices from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: get_devices from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: get_devices from Breeze not received, error: "+str(ge))
                return None
            
def getTasks(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getTasks with parameters {QUERY_PARAMS}")
            if QUERY_PARAMS['turbines'] is not None:
                return greenbyte_client.plan.list_tasks(QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampEnd'],
                            device_ids=QUERY_PARAMS['turbines'],
                            category_ids=QUERY_PARAMS['categoryIds'],
                            state=QUERY_PARAMS['state'],fields=None,page_size=QUERY_PARAMS['pageSize'],page=QUERY_PARAMS['page'],use_utc=False)
            elif QUERY_PARAMS['sites'] is not None:
                return greenbyte_client.plan.list_tasks(QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampEnd'],
                            site_ids=QUERY_PARAMS['sites'],
                            category_ids=QUERY_PARAMS['categoryIds'],
                            state=QUERY_PARAMS['state'],fields=None,page_size=QUERY_PARAMS['pageSize'],page=QUERY_PARAMS['page'],use_utc=False)
            else:
                return greenbyte_client.plan.list_tasks(QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampEnd'],
                            category_ids=QUERY_PARAMS['categoryIds'],
                            state=QUERY_PARAMS['state'],fields=None,page_size=QUERY_PARAMS['pageSize'],page=QUERY_PARAMS['page'],use_utc=False)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: list_tasks from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: list_tasks from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: list_tasks from Breeze not received, error: "+str(ge))
                return None
            
def getTaskCategories(greenbyte_client,LOGGER):
    tries=0
    while tries<3:
        try:
            if tries==0:
                LOGGER.debug(f"Running getTaskCategories")
            return greenbyte_client.plan.list_task_categories()
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: list_task_categories from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.error(f"ERROR: list_task_categories from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.error(f"ERROR: list_task_categories from Breeze not received, error: "+str(ge))
                return None