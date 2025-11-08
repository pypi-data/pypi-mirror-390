import logging
import random
from socket import gethostname
from azure.data.tables import TableServiceClient#, TableEntity
from opencensus.ext.azure.log_exporter import AzureLogHandler

class TableLogHandler(logging.Handler):
    def __init__(self, account_name, account_key, table_name, instrumentation_key=None):
        self.self_logging=False
        try:
            properties = {'custom_dimensions': {'table': table_name, 'mystorageaccountname': account_name}}
            #creating logger for self, so that it is visible in Azure Insights
            if instrumentation_key is not None:
                logger = logging.getLogger('azure-insights')
                logger.addHandler(AzureLogHandler(connection_string=f'InstrumentationKey={instrumentation_key}'))
                self.self_logging=True
        except:
            pass

        try:
            logging.Handler.__init__(self)
            #Connection string to the Table 'table_name' in Azure Storage Account 'account_name' with the authenticatoin key 'account_key'
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            
            #Using TableServiceClient function from the azure-data-tables library to create table_client
            if self.self_logging:
                logger.debug(f'Creating TableServiceClient for table {table_name}', extra=properties)
            self.service = TableServiceClient.from_connection_string(conn_str=connection_string)
            self.table_client = self.service.get_table_client(table_name=table_name)
            
            #Getting hostname of the system, it will be stored in a log entry
            self.hostname = gethostname()
            
            #PartitionKey must be present in an entity
            self.partition_key_formatter = logging.Formatter('%(asctime)s', '%Y%m%d%H%M')
            
            #Formatter for the row key
            self.row_key_formatter = logging.Formatter('%(created)f_%(process)d_%(thread)d_%(lineno)d', '%Y%m%d%H%M%S')
            if self.self_logging:
                logger.debug(f'TableServiceClient for table {table_name} created', extra=properties)
        except Exception as ex:
            if self.self_logging:
                logger.exception(f'Failed creating TableServiceClient for table {table_name}: {ex}', extra=properties)
    
    def emit(self, record):
        try:
            #Creating an entry for the log
            record.hostname = self.hostname
            entity = {}
            entity['PartitionKey'] = self.partition_key_formatter.format(record)
            entity['RowKey'] = self.row_key_formatter.format(record)+"_R"+str(random.randint(0,999999))#Adding a random number, otherwise we get duplicates for some reason!
            dict_log=record.__dict__
            entity['level'] = dict_log['levelname']
            entity['hostname'] = self.hostname
            entity['process'] = f"{dict_log['module']}.{dict_log['processName']}"
            entity['message'] = self.format(record)
            #Storing the entry in the table
            self.table_client.create_entity(entity)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print(e)
            #self.handleError(record)
            pass