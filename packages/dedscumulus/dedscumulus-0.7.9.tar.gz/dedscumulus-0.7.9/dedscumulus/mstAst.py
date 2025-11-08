import msal
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import pyodbc
from sqlalchemy import create_engine, text
import struct
import smtplib
import time
import urllib
import pandas as pd
import numpy as np
from decimal import Decimal


def getAssetTypes(DB_CRED,logger,trust='no',encrypt='yes',timeout=30):
    current_row=''
    assetTypes={}
    try:
        logger.debug("Starting getAssetTypes")
        errors=0
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT [AssetTypeId],[ExternalName] FROM [dbo].[mstAssetType] WHERE [ExternalName] IS NOT NULL;")
                        for row in cursor:
                            current_row=str(row)
                            assetTypes[row[1]]=row[0]
                        return assetTypes
            except Exception as pe:
                errors+=1
                time.sleep(0.05)
        log_text="mstAst.getAssetTypes Failed 3 times, stopping execution"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.getAssetTypes Failed, error: {e1}, current_row: {current_row}"
        logger.error(log_text)
        return None


def getBrzAssetIds(DB_CRED,LOGGER,trust='no',encrypt='yes',timeout=30):
    assetIds={}
    try:
        with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
            with conn.cursor() as cursor:
                cursor.execute("DECLARE @turbineid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Turbine');SELECT [AssetId],JSON_VALUE([SystemIds], '$.brz') AS [brzId],JSON_VALUE([Info], '$.ratedPower') AS [RatedPower] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@turbineid AND JSON_VALUE([SystemIds], '$.brz') IS NOT NULL;")
                for row in cursor:
                    item={}
                    item['AssetId']=row[0]
                    item['RatedPower']=row[2]
                    assetIds[row[1]]=item
        if len(assetIds)>0:
            return assetIds
        log_text="mstAst.getBrzAssetIds returned zero results"
        LOGGER.warning(log_text)
        return None
    except Exception as e1:
        log_text="mstAst.getBrzAssetIds Failed, error: "+str(e1)
        LOGGER.error(log_text)
        return None


def executeCommand(DB_CRED,sql,logger,trust='no',encrypt='yes',timeout=30):
    #this function returns negatie values in case of an error!!!
    try:
        #logger.debug(f"mstAst.executeCommand / Executing an SQL command")
        errors=0
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    with conn.cursor() as cursor:
                        logger.debug(f"mstAst.executeCommand / sql: {sql[:5000]}")
                        cursor.execute(sql)
                        rows=int("{}".format(cursor.rowcount))
                        logger.debug(f"mstAst.executeCommand / Received {rows} rows from cursor")
                        if rows==0:
                            #logger.debug(f"mstAst.executeCommand / 0 rows from cursor, returning 1")
                            return 1#so that we know that execution was successful
                        return rows
            except Exception as s1:
                if errors==0:
                    logger.warning(f"mstAst.executeCommand / first failure: "+str(s1)[:5000]+", command: "+str(sql[:2500]))
                if "Violation of UNIQUE KEY constraint" in s1.args[1]:
                    logger.warning(f"mstAst.executeCommand / Violation of UNIQUE KEY constraint detected")
                    return -2
                if "The number of row value expressions in the INSERT statement exceeds the maximum allowed number of 1000" in s1.args[1]:
                    logger.warning(f"mstAst.executeCommand / INSERT statement exceeds the maximum allowed number of 1000")
                    return -3
                errors+=1
                time.sleep(0.05)
        logger.error("mstAst.executeCommand Failed 3 times, stopping execution, last command: "+str(sql[:2500]))
        return -1
    except Exception as e1:
        logger.error(f"mstAst.executeCommand Failed, error: {e1.args[1]}, sql: {sql[:2500]}")
        return -1


def executeSelect(DB_CRED,sql,logger,trust='no',encrypt='yes',pandas_df=False,timeout=30):
    selectRows=[]
    try:
        logger.debug(f"mstAst.executeSelect / Executing {sql}")
        errors=0
        error_text=None
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    if pandas_df:
                        df = pd.read_sql_query(sql,con=conn)
                        return df
                    else:
                        with conn.cursor() as cursor:
                            cursor.execute(sql)
                            for row in cursor:
                                selectRows.append(row)
                            return selectRows
            except Exception as pe:
                error_text=str(pe)
                errors+=1
                time.sleep(0.05)
        log_text="mstAst.executeSelect Failed 3 times, stopping execution"
        if error_text is not None:
            log_text+=f". Last thrown error: {error_text}"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.executeSelect Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return None


def executeMultipleSelect(DB_CRED,sqls,logger,trust='no',encrypt='yes',pandas_df=False,timeout=30):
    try:
        logger.debug(f"mstAst.executeMultipleSelect ({len(sqls)} selects)")
        errors = 0
        error_text = None
        results = []
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    for sql in sqls:
                        if pandas_df:
                            df = pd.read_sql_query(sql,con=conn)
                            results.append(df)
                        else:
                            selectRows=[]
                            with conn.cursor() as cursor:
                                cursor.execute(sql)
                                for row in cursor:
                                    selectRows.append(row)
                                results.append(selectRows)
                    #logger.debug(f"mstAst.executeMultipleSelect; returning result array with {len(results)} items")
                    return results
            except Exception as pe:
                error_text=str(pe)
                errors+=1
                time.sleep(0.05)
        log_text="mstAst.executeMultipleSelect Failed 3 times, stopping execution"
        if error_text is not None:
            log_text+=f". Last thrown error: {error_text}"
        logger.error(log_text)
        return results
    except Exception as e1:
        log_text=f"mstAst.executeMultipleSelect Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return []


def createSQLconnection(CREDS,LOGGER):
    try:
        tenant_id = CREDS["tenant"]
        clientId = CREDS["client_id"]
        clientSecret = CREDS["client_secret"]
        server = CREDS['db_server']
        database = CREDS['database']            
        driver = "{ODBC Driver 18 for SQL Server}"
        authorityHostUrl = "https://login.microsoftonline.com" 
        authority_url = (authorityHostUrl + '/' + tenant_id)

        app = msal.ConfidentialClientApplication(
        client_id=clientId,
        client_credential=clientSecret,
        authority=authority_url
        )

        # Step 2: Acquire token for Azure SQL
        scope = ["https://database.windows.net//.default"]  # <-- Note the double slash!
        result = app.acquire_token_for_client(scopes=scope)

        if "access_token" not in result:
            raise Exception("Failed to acquire token: " + result.get("error_description", "Unknown error"))

        access_token = result["access_token"]

        # Step 3: Prepare access token for SQL Server connection
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        tokenb = bytes(access_token, "UTF-8")
        exptoken = b''.join(bytes((b, 0)) for b in tokenb)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken

        # Step 4: Connect to Azure SQL with token
        connString = f"Driver={driver};SERVER={server};DATABASE={database}"
        conn = pyodbc.connect(connString, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct})

        return conn
    except Exception as ec:
        LOGGER.error(f"mstAst.createSQLconnection Error: "+str(ec))
        return None


def getAssetParameter(DB_CRED,assetId,parameter,logger,subParameter=None,trust='no',encrypt='yes',timeout=30):
    try:
        logger.debug("Starting getAssetParameter")
        errors=0
        while errors<3:
            try:
                if subParameter is None:
                    sql=f"SELECT [{parameter}] FROM [dbo].[mstAssets] WHERE [AssetId]={assetId};"
                else:
                    sql=f"SELECT JSON_VALUE([{parameter}],'$.{subParameter}') FROM [dbo].[mstAssets] WHERE [AssetId]={assetId};"
                #assetTypes={}
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        for row in cursor:
                            return row[0]
                        return None#if no rows are returned, return none
            except:
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getAssetParameter Failed 3 times, stopping execution"
    except Exception as e1:
        log_text=f"mstAst.getAssetParameter Failed, error: {e1:[:1000]}"
        logger.error(log_text)


def getColumnEntry(DB_CRED,getWhat,tableFrom,whereFilter,equalsWhat,string,logger,trust='no',encrypt='yes',timeout=30):
    try:
        logger.debug(f"mstAst.getColumnEntry / Getting {getWhat} from {tableFrom} on {DB_CRED['db_server']}.{DB_CRED['database']}")
        errors=0
        exc_text=""
        while errors<3:
            try:
                if string==1:
                    sql="SELECT "+getWhat+" FROM [dbo].["+tableFrom+"] WHERE ["+whereFilter+"]='"+equalsWhat+"';"
                else:
                    sql="SELECT "+getWhat+" FROM [dbo].["+tableFrom+"] WHERE ["+whereFilter+"]="+str(equalsWhat)+";"
                logger.debug(f"mstAst.getColumnEntry / SQL: {sql}")
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        for row in cursor:
                            logger.debug(f"mstAst.getColumnEntry OK, result: {row[0]}")
                            return row[0]
                        return None#if no rows are returned, return none
            except Exception as e2:
                log_text=f"mstAst.getColumnEntry Failed, error2: {e2}"
                exc_text=str(e2)[:500]
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getColumnEntry Failed 3 times, stopping execution, error: {exc_text}"
        return None
    except Exception as e1:
        log_text=f"mstAst.getColumnEntry Failed, error1: {e1}"
        logger.error(log_text)
        return None


def buildMimeMessage(sender, subject, body, to_address, prio, text_type, logger, cc_address, bcc_address):
    try:
        msg = MIMEMultipart('html')
        msg['From'] = sender
        msg['To'] = to_address
        msg['Cc'] = cc_address
        msg['Bcc'] = bcc_address
        msg['Subject'] = subject
        msg['X-Priority'] = prio
        msg.attach(MIMEText(body, text_type))
        return msg
    except Exception as e1:
        logger.error(f"mstAst.buildMimeMessage Failed, error: "+str(e1)[:1000])
        return None


def sendEmail(CREDS, subject, body, to_address, prio, text_type, logger, cc_address=None, bcc_address=None):
    try:
        #text_type: html, plain
        #prio: 1 (high), 3 (normal), 5 (low)
        logger.warning("Starting sendEmail w/ BasicAuth (Not using OAuth!)")
        message = buildMimeMessage(CREDS["email_username"], subject, body, to_address, str(prio), text_type, logger, cc_address, bcc_address)
        if message is not None:
            exch=smtplib.SMTP(CREDS["email_server"], CREDS["email_port"])
            exch.starttls()
            exch.login(CREDS["email_username"], CREDS["email_password"])
            exch.send_message(message)
            exch.quit()
            return 0
        return 1
    except Exception as e1:
        log_text=f"mstAst.sendEmail w/ BasicAuth Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return -1


def getSetting(CREDS,version,settingName,systemShortName,logger,trust='no',encrypt='yes',timeout=30):
    #this version of the function is using one mstSettings table instead of multiple ones like in the past
    try:
        logger.debug("Starting getSetting")
        errors=0
        while errors<3:
            try:
                sql=f"DECLARE @sysid INT=(SELECT [systemId] from [mstSystems] WHERE [shortName]='{systemShortName}');SELECT [Setting] FROM [dbo].[mstSettings] WHERE [settingVersion]={version} AND [settingName]='{settingName}' and [systemId]=@sysid;"
                logger.debug(f"SQL: {sql}")
                conn_string='Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}"
                logger.debug(f"Connection: {conn_string}")
                with pyodbc.connect(conn_string) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        return cursor.fetchone()[0]
            except Exception as pe:
                logger.error(f"Failed getting setting: {pe}")
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getSetting Failed 3 times, stopping execution"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.getSetting Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return None


def dfToDB2(CREDS,table,df,chunkSize,logger,trust='yes',encrypt='yes',timeout=60):
    try:
        try:
            timeout=str(CREDS['timeout'])
        except:
            pass
        logger.debug(f"Creating connection string")
        conn_str=urllib.parse.quote_plus(r'Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd='+CREDS['db_password']+';Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}")
        conn='mssql+pyodbc:///?odbc_connect={}'.format(conn_str)
        engine=create_engine(conn, fast_executemany=True, echo=False)
        #engine=create_engine(conn, fast_executemany=False, echo=False)
        #result=df.to_sql(table, engine, if_exists='append', chunksize=chunkSize, index=False, method='multi')
        logger.debug(f"dfToDB2 executing")
        timestampStart = datetime.now()
        result=df.to_sql(table, engine, if_exists='append', chunksize=chunkSize, index=False)
        timestampEnd=datetime.now()
        runTime=str(timestampEnd-timestampStart)[:-7]
        size=len(df.index)
        logger.debug(f"mstAst.dfToDB2 storing to table {table} ended with chunksize: {chunkSize}, result: {result}, size: {size} in {runTime}")

        if isinstance(result, int) or result is None:
            return 0
        else:
            logger.warning(f"mstAst.dfToDB2 storing to table {table} ended with result: {result}, size: {size}, returning 0")
        if size>chunkSize:
            logger.debug(f"mstAst.dfToDB2 storing to table {table} ended with result: {result}, size: {size}, returning 0")
        return 0
    except Exception as e1:
        logger.error(f"mstAst.dfToDB2, storing to table {table} failed, error: "+str(e1)[:5000])
        return 1


def _sql_literal(value):
    """Convert a Python value into a safe SQL literal for SQL Server."""
    if pd.isna(value):
        return "NULL"
    if isinstance(value, np.generic):
        value = value.item()
    if value is None:
        return "NULL"
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return "'" + escaped + "'"
    if isinstance(value, (datetime, date)):
        return f"'{value.isoformat(sep=' ')}'"
    if isinstance(value, bool):
        return '1' if value else '0'
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    return value
                                  

def dfToDB3(CREDS, table, df, merge_keys, chunkSize, logger, trust='yes', encrypt='yes', timeout=60):
    """
    Performs a direct MERGE (UPSERT) of a pandas DataFrame into SQL Server
    without using any temporary or staging tables.
    Works best for small-to-medium DataFrames.
    """
    try:
        # ---- Build connection string ----
        conn_str = urllib.parse.quote_plus(
            f"Driver={CREDS['driver']};"
            f"Server=tcp:{CREDS['db_server']},1433;"
            f"Database={CREDS['database']};"
            f"Uid={CREDS['db_user']};"
            f"Pwd={CREDS['db_password']};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust};"
            f"Connection Timeout={timeout};"
        )
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}", fast_executemany=True, echo=False)
        logger.debug(f"Connecting to {CREDS['database']} for merge into {table}")

        all_cols = list(df.columns)
        set_cols = [c for c in all_cols if c not in merge_keys]

        merge_condition = " AND ".join([f"target.[{c}] = source.[{c}]" for c in merge_keys])
        update_clause = ", ".join([f"target.[{c}] = source.[{c}]" for c in set_cols])
        insert_cols = ", ".join([f"[{c}]" for c in all_cols])
        insert_values = ", ".join([f"source.[{c}]" for c in all_cols])

        with engine.begin() as connection:
            timestampStart = datetime.now()
            total_rows = len(df)
            logger.debug(f"Starting direct MERGE for {total_rows} rows into {table}")

            for start in range(0, total_rows, chunkSize):
                chunk = df.iloc[start:start + chunkSize]
                if chunk.empty:
                    continue

                # ---- Build VALUES clause safely ----
                rows = []
                for row in chunk.itertuples(index=False, name=None):
                    literals = [_sql_literal(v) for v in row]
                    rows.append("(" + ", ".join(literals) + ")")
                values_clause = ",\n".join(rows)

                # ---- Compose MERGE SQL ----
                sql_merge = f"""
                MERGE {table} AS target
                USING (
                    VALUES
                    {values_clause}
                ) AS source ({', '.join(f'[{c}]' for c in all_cols)})
                ON {merge_condition}
                WHEN MATCHED THEN
                    UPDATE SET {update_clause}
                WHEN NOT MATCHED BY TARGET THEN
                    INSERT ({insert_cols})
                    VALUES ({insert_values});
                """

                connection.execute(text(sql_merge))
                #logger.debug(f"Merged chunk {start}–{start + len(chunk) - 1} into {table}")

            timestampEnd = datetime.now()
            logger.debug(f"Completed MERGE for {table} in {str(timestampEnd - timestampStart)[:-7]}")
        return 0

    except Exception as e:
        logger.error(f"dfToDB3 failed for {table}: {str(e)[:2000]}")
        return 1


def getVaultSecret(vault_name,secret_name,csc=None,logger=None):
    try:
        if csc is None:
            credential = DefaultAzureCredential()
        else:
            credential = ClientSecretCredential(csc['tenant'], csc['client_id'], csc['client_secret'])
        client = SecretClient(vault_url=f"https://{vault_name}.vault.azure.net", credential=credential)
        return client.get_secret(secret_name).value
    except Exception as e1:
        if logger is not None:
            logger.error(f"mstAst.getVaultSecret Failed, error: {e1}[:500]")
        else:
            print(f"mstAst.getVaultSecret Failed, error: {e1}")
        return None


def insertSLALog(DB_CRED,service,function,factor,ex_time,logger,trust='no',encrypt='yes',timeout=30):
    try:
        errors=0
        sql="Not set"
        error="Not set"
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt='+encrypt+';TrustServerCertificate='+trust+';Connection Timeout='+f"{timeout}") as conn:
                    with conn.cursor() as cursor:
                        if ex_time<1:#if a quick function, we set it to 1 second anyway
                            ex_time=1
                        if isinstance(service, int):#in case of use a hard-coded id
                            sql=f"DECLARE @serviceid INT = {service};"
                        else:
                            sql=f"DECLARE @serviceid INT = (SELECT [serviceId] FROM [dbo].[mstServices] WHERE [serviceName]='{service}');"
                        sql+=f"INSERT INTO [dbo].[afaUsageLog] ([TS_INSERTED],[azureFunctionName],[serviceId],[costFactor],[executionTime]) "
                        sql+=f"VALUES (CURRENT_TIMESTAMP, '{function}', @serviceid, {factor}, {ex_time});"

                        logger.debug(f"mstAst.insertSLALog / sql: {sql}")
                        cursor.execute(sql)
                        rows=int("{}".format(cursor.rowcount))
                        logger.debug(f"mstAst.insertSLALog / Received {rows} rows from cursor")
                        if rows==0:
                            #logger.debug(f"mstAst.executeCommand / 0 rows from cursor, returning 1")
                            return 1#so that we know that execution was successful
                        return rows
            except Exception as s1:
                if errors==0:
                    logger.debug(f"mstAst.insertSLALog / first failure: "+str(s1)+", command: "+sql)
                    error = f'{s1}'
                errors+=1
                time.sleep(0.05)
        logger.error(f"mstAst.insertSLALog Failed 3 times, stopping execution, last command: {sql}, error: {error}")
        return -1
    except Exception as e1:
        logger.error(f"mstAst.insertSLALog Failed, error: {e1.args[1]}, service: {service}")
        return -1


def writeFileDBX(path, file_name, data, logger, useJson=False, usePickle=False):
    try:
        bytes_written=-1
        logger.debug(f"Writing file {file_name} to {path}")
        full_path = rf'{path}/{file_name}'
        if not os.path.isdir(path):
            logger.debug(f"Creating folder {path}")
            os.makedirs(path, exist_ok=True)
        with open(full_path, mode='w', encoding="utf-8") as f:
            if useJson:
                json.dump(data, f)
                bytes_written=len(str(data))
            elif usePickle:
                data.to_pickle(f)
                bytes_written=len(str(data))
            else:
                bytes_written=f.write(data)
            k="bytes"
            if bytes_written>10000:
                bytes_written/=1024
                k="kB"
            logger.debug(f"File '{file_name}' written ({round(bytes_written,0)} {k})")
    except Exception as e:
        logger.error(f"mstAst.writeFileDBX Failed, error: "+str(e))
    finally:
        return bytes_written