

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict
from totopubsub.logger import Logger
from totopubsub.model import Context, TotoMessage, TotoMessageData

class PubSub(ABC):
    
    def __init__(self, context: Context, pubsub_impl_name: str):
        super().__init__()
        
        self.context = context
        self.impl_name = pubsub_impl_name
    
    def publish_message(self, topic_name: str, message: TotoMessageData) -> Dict:
        """
        Publishes a message to the specified topic

        Args:
            topic_name (str): The name of the topic to publish to
            message (TotoMessageData): The message to publish

        Returns:
            Dict: A dictionary containing the result of the publish operation
        """
        logger = Logger()
        cid = self.context.correlation_id

        # Convert TotoMessageData to TotoMessage
        toto_message = TotoMessage(
            timestamp=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            cid=cid,
            id=message.id,
            type=message.event_name,
            msg=message.msg,
            data=message.data
        )

        logger.log(cid, f"Preparing to publish message on {self.impl_name} of type [ {toto_message.type} ] to topic [ {topic_name} ] with id [ {toto_message.id} ]")

        result = self._publish_message(topic_name, toto_message)

        logger.log(cid, f"Successfully published message on {self.impl_name} of type [ {toto_message.type} ] to topic [ {topic_name} ] with id [ {toto_message.id} ]. Result: {result}")
        
        return result

    @abstractmethod
    def _publish_message(self, topic_name: str, message: TotoMessage) -> Dict:
        """
        Publish a message to the specified topic.
        
        Args:
            topic_name: The name of the topic to publish to
            message: The TotoMessage to publish
            
        Returns:
            str: The message ID of the published message
            
        Raises:
            Exception: If publishing fails
        """
        pass
    
class PubSubFactory:

    @staticmethod
    def create_pubsub(context: Context):
        """
        Create a PubSub instance based on the HYPERSCALER environment variable.
        
        Args:
            exec_context: Required for GCP implementation
            
        Returns:
            PubSub: An instance of the appropriate PubSub implementation
        """
        # Import here to avoid circular imports
        from totopubsub.impl.aws.sns import SNS
        from totopubsub.impl.gcp.gcppubsub import GCPPubSub
        
        # 1. Get the environment 
        hyperscaler: str = context.hyperscaler
        region: str = context.region

        # 2. Create the PubSub according to the hyperscaler
        if hyperscaler == 'aws':
            return SNS(context, "AWS SNS")
        elif hyperscaler == 'gcp':
            return GCPPubSub(context, "GCP PubSub")

        raise Exception(f"PubSub for hyperscaler {hyperscaler} is not implemented yet.")
