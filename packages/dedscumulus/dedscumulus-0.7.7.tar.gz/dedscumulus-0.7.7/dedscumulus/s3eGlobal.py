from RequestHandler import requests_retry_session as req
import requests
import json
#import dedscumulus.RequestHandler as req

def getData(CREDS,PARAMS,LOGGER):
    try:
        #s3e_url='https://api.3elabs.eu/solardata'
        s3e_url=PARAMS['s3e_url']
        output=0
        #'?latitude=50.8347&longitude=3.3017&inclination=10&azimuth=153&start=2023-04-01&end=2023-04-30&variables=global_inclined&resolution=d&output=csv&version=1.4&authorization=58a581bc12d5aa0001381f0f42b136da4d3145f54b6bc2d9d4b0940d'

        if PARAMS['latitude'] is None or PARAMS['longitude'] is None or PARAMS['variables'] is None or PARAMS['resolution'] is None or CREDS['s3e_token'] is None:
            LOGGER.error(f"ERROR: s3eGlobal.getData could not retrieve data, not all parameters are provided!")
            return None
        
        resolutions=['15min','30min','h','d','m']
        if PARAMS['resolution'] not in resolutions:
            LOGGER.warning(f"WARNING: s3eGlobal.getData resolution provided is potentially invalid ({PARAMS['resolution']})")
        
        variables=['global_inclined','global_horizontal','diffuse_horizontal','direct_normal','ambient_temperature','wind_speed','wind_direction']
        if PARAMS['variables'] not in variables:
            LOGGER.warning(f"WARNING: s3eGlobal.getData variables provided is potentially invalid ({PARAMS['variables']})")

        prms={'latitude': PARAMS['latitude'],
            'longitude': PARAMS['longitude'],
            'variables': PARAMS['variables'],
            'resolution': PARAMS['resolution'],
            'authorization': CREDS['s3e_token']
              }
        if PARAMS['inclination'] is not None:
            prms['inclination']=PARAMS['inclination']
        if PARAMS['azimuth'] is not None:
            prms['azimuth']=PARAMS['azimuth']
        if PARAMS['start'] is not None:
            prms['start']=PARAMS['start']
        if PARAMS['end'] is not None:
            prms['end']=PARAMS['end']
        if PARAMS['output'] is not None:
            prms['output']=PARAMS['output']
            if PARAMS['output']=='csv':
                output=1
        if PARAMS['version'] is not None:
            prms['version']=PARAMS['version']

        LOGGER.debug(f"s3eGlobal.getData Getting data with parameters: {prms}")

        with req.requests_retry_session(requests.Session(), backoff_factor=2, status_forcelist=(500, 502, 504)).post(s3e_url, data=prms) as r:
            if(r.status_code==200):
                LOGGER.debug(f"s3eGlobal.getData Data retrieved, length: {len(r.text)}")
                if output==0:
                    return json.loads(r.text)
                return r.text
            else:
                LOGGER.error(f"s3eGlobal.getData Failed, response code: {r.status_code}, text: {r.text}")
                return None
    except Exception as ge:
        LOGGER.error(f"ERROR: s3eGlobal.getData erred: "+str(ge))
        return None
