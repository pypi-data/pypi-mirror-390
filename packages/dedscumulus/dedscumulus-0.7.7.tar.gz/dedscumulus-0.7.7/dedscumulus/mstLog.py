import logging
from .TableLogHandler import TableLogHandler

class Log:
    def __init__(self, CREDS, log_table, log_level, script=None):
        #logger.setLevel(logging.DEBUG)
        #notset=0
        #trace=5\does not exist!
        #debug=10
        #info=20
        #warning=30
        #error=40
        #critical=50
        try:
            CREDS["instrumentation_key"]
        except:
            CREDS["instrumentation_key"]=None

        if script is None:
            logger_var = log_table
        else:
            logger_var = script
        
        self.logger = logging.getLogger(logger_var)
        self.logger.setLevel(int(log_level))
        if len(self.logger.handlers)>0:
            self.logger.handlers.clear()
        self.azure_blob_handler = TableLogHandler(account_name=CREDS["mystorageaccountname"],
                                            account_key=CREDS["mystorageaccountkey"],
                                            table_name=log_table,
                                            instrumentation_key=CREDS["instrumentation_key"])
        self.logger.addHandler(self.azure_blob_handler)