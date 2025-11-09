import json
import os
from typing import Dict, Any
from totopubsub.logger import Logger
from totopubsub.model import TotoMessage, Context
from totopubsub.pubsub import PubSub
from google.cloud import pubsub_v1
import google.auth


class GCPPubSub(PubSub):

    def __init__(self, context: Context, pubsub_impl_name: str):

        super().__init__(context, pubsub_impl_name)

        # Only create one publisher client
        self.credentials, self.project_id = google.auth.default()
        self.publisher = pubsub_v1.PublisherClient(credentials=self.credentials)
    
    def _publish_message(self, topic_name: str, message: TotoMessage) -> Dict:
        """
        Publish a message to a GCP Pub/Sub topic.
        
        Args:
            topic_name: The name of the Pub/Sub topic
            message: TotoMessage protocol object containing the message data
            
        Returns:
            str: The message ID of the published message
            
        Raises:
            Exception: If publishing fails
        """
        logger = Logger()
        
        # Convert TotoMessage to dict for serialization
        message_dict = {
            "timestamp": message.timestamp,
            "cid": message.cid,
            "id": message.id,
            "type": message.type,
            "msg": message.msg,
            "data": message.data
        }

        json_message = json.dumps(message_dict)

        try:

            topic_path = self.publisher.topic_path(os.getenv('GCP_PID'), topic_name)

            future = self.publisher.publish(topic_path, data=json_message.encode('utf-8'))

            # Only call result() if we need the message ID immediately
            # For fire-and-forget scenarios, consider removing this
            message_id = future.result(timeout=30.0)  # Add timeout to prevent indefinite blocking

            return {"messageId" : message_id}

        except Exception as e:
            
            error_msg = f"Publishing the event [ {message.type} ] failed. Error: {str(e)}"
            
            logger.log(self.context.correlation_id, error_msg, "error")
            logger.log(self.context.correlation_id, f"Failed message: [ {json_message} ]", "error")
            
            raise Exception(error_msg) from e