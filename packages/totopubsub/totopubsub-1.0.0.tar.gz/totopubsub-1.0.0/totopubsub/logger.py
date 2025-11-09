from datetime import datetime

class Logger: 
    
    def log(self, cid: str, msg: str) -> None: 
        """ Logs in console out a message 

        Args:
            cid (str): the Correlation Id
            msg (str): the message to be logged
        """
        # Get the current timestamp
        current_timestamp = datetime.now()
        
        # Format it
        formatted_timestamp = current_timestamp.strftime('%Y.%m.%d %H:%M:%S,%f')[:-3]
        
        # Log
        print(f"[Toto PubSub] - [{cid}] - [{formatted_timestamp}] - {msg}")