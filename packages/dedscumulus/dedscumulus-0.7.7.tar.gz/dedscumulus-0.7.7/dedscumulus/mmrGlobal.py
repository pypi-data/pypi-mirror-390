from dedscumulus import mstAst as mstAst
import time


def getAssets(CREDS,LOGGER):
    try:
        LOGGER.debug("Starting getAssetsMimir")
        errors=0
        while errors<3:
            try:
                conn=mstAst.createSQLconnection(CREDS, LOGGER)
                cursor = conn.cursor()
                sql="SELECT [ID],[NAME],[PROJECT_CODE],[FRM_ASSET_ID],[PRIORITY],[IS_ACTIVE],[COUNTRY_ID],[LONGITUDE],[LATITUDE],[ENERGY_TYPE]"
                sql+=",[PLANT_TYPE],[POWER_AC],[POWER_DC],[MONITORING_SYSTEM_ID],[NETWORK_OPERATOR],[SERVICE_COMPANY_ID] FROM [curated].[ASSET_MAIN];"
                cursor.execute(sql)
                assetsMimir={}
                row = cursor.fetchone()
                while row:
                    assetsMimir[row[0]]={}
                    assetsMimir[row[0]]['name']=row[1]
                    assetsMimir[row[0]]['projectCode']=row[2]
                    assetsMimir[row[0]]['FRMID']=row[3]
                    assetsMimir[row[0]]['priority']=row[4]
                    assetsMimir[row[0]]['active']=row[5]
                    assetsMimir[row[0]]['countryId']=row[6]
                    assetsMimir[row[0]]['longitude']=row[7]
                    assetsMimir[row[0]]['latitude']=row[8]
                    assetsMimir[row[0]]['energyType']=row[9]
                    assetsMimir[row[0]]['plantType']=row[10]
                    assetsMimir[row[0]]['powerAC']=row[11]
                    assetsMimir[row[0]]['powerDC']=row[12]
                    assetsMimir[row[0]]['monSysId']=row[13]
                    assetsMimir[row[0]]['gridOperator']=row[14]
                    assetsMimir[row[0]]['serviceCompanyId']=row[15]
                    #assetsMimir[row[0]]['plantType']=row[16]
                    #assetsMimir[row[0]]['plantType']=row[17]
                    #assetsMimir[row[0]]['plantType']=row[18]
                    #assetsMimir[row[0]]['plantType']=row[19]
                    row = cursor.fetchone()
                return assetsMimir
            except:
                errors+=1
                time.sleep(0.05)
        LOGGER.error(f"mstAst.getAssetsMimir Failed 3 times, stopping execution")
        return None
    except Exception as e1:
        LOGGER.error(f"mstAst.getAssetsMimir Failed, error: {e1:[:1000]}")
        return None

def getCountries(CREDS,LOGGER):
    try:
        LOGGER.debug("Starting getCountriesMimir")
        errors=0
        while errors<3:
            try:
                conn=mstAst.createSQLconnection(CREDS, LOGGER)
                cursor = conn.cursor()
                sql="SELECT [ID],[ISO2_CODE],[NAME] FROM [dim].[COUNTRY] WHERE [ENABLED]=1;"
                cursor.execute(sql)
                countriesMimir={}
                row = cursor.fetchone()
                while row:
                    countriesMimir[row[0]]={}
                    countriesMimir[row[0]]['iso2']=row[1]
                    countriesMimir[row[0]]['name']=row[2]
                    row = cursor.fetchone()
                return countriesMimir
            except:
                errors+=1
                time.sleep(0.05)
        LOGGER.error(f"mstAst.getCountriesMimir Failed 3 times, stopping execution")
        return None
    except Exception as e1:
        LOGGER.error(f"mstAst.getCountriesMimir Failed, error: {e1:[:1000]}")
        return None

def getEnergyTypes(CREDS,LOGGER):
    try:
        LOGGER.debug("Starting getEnergyTypes")
        errors=0
        while errors<3:
            try:
                conn=mstAst.createSQLconnection(CREDS, LOGGER)
                cursor = conn.cursor()
                sql="SELECT [ID],[NAME] FROM [dim].[ENERGY_TYPE] WHERE [ENABLED]=1;"
                cursor.execute(sql)
                countriesMimir={}
                row = cursor.fetchone()
                while row:
                    countriesMimir[row[0]]={}
                    countriesMimir[row[0]]['name']=row[1]
                    row = cursor.fetchone()
                return countriesMimir
            except:
                errors+=1
                time.sleep(0.05)
        LOGGER.error(f"mstAst.getEnergyTypes Failed 3 times, stopping execution")
        return None
    except Exception as e1:
        LOGGER.error(f"mstAst.getEnergyTypes Failed, error: {e1:[:1000]}")
        return None
    
def getLegalEntities(CREDS,LOGGER):
    try:
        LOGGER.debug("Starting getEnergyTypes")
        errors=0
        while errors<3:
            try:
                conn=mstAst.createSQLconnection(CREDS, LOGGER)
                cursor = conn.cursor()
                sql="SELECT [ID],[NAME],[SHORT_NAME] FROM [dim].[LEGAL_ENTITY] WHERE [ENABLED]=1;"
                cursor.execute(sql)
                legalEntitiesMimir={}
                row = cursor.fetchone()
                while row:
                    legalEntitiesMimir[row[0]]={}
                    legalEntitiesMimir[row[0]]['name']=row[1]
                    legalEntitiesMimir[row[0]]['shortName']=row[2]
                    row = cursor.fetchone()
                return legalEntitiesMimir
            except:
                errors+=1
                time.sleep(0.05)
        LOGGER.error(f"mstAst.getEnergyTypes Failed 3 times, stopping execution")
        return None
    except Exception as e1:
        LOGGER.error(f"mstAst.getEnergyTypes Failed, error: {e1:[:1000]}")
        return None