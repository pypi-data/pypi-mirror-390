from ast import Dict
import os
import boto3
import json
from totopubsub.model import TotoMessage
from totopubsub.pubsub import PubSub
from totopubsub.model import Context


class SNS(PubSub):
    
    def __init__(self, context: Context, pubsub_impl_name: str):
        super().__init__(context, pubsub_impl_name)
        
        self.sns_client = boto3.client('sns', region_name=context.region)
        self.sts_client = boto3.client('sts', region_name=context.region)

    def _publish_message(self, topic_name: str, message: TotoMessage) -> Dict:
        """
        Publish a message to an SNS topic.
        
        Args:
            topic_name: The name of the SNS topic (will be used to construct ARN or can be full ARN)
            message: TotoMessage protocol object containing the message data
            
        Returns:
            str: The message ID of the published message
            
        Raises:
            Exception: If publishing fails
        """
        try:
            # Convert TotoMessage to dict for serialization
            message_dict = {
                "timestamp": message.timestamp,
                "cid": message.cid,
                "id": message.id,
                "type": message.type,
                "msg": message.msg,
                "data": message.data
            }

            # If topic_name is not an ARN, construct it
            if not topic_name.startswith('arn:aws:sns:'):

                # Get AWS account ID and region from STS
                account_id = self.sts_client.get_caller_identity()['Account']
                
                region = self.sns_client.meta.region_name

                topic_arn = f"arn:aws:sns:{region}:{account_id}:{topic_name}"

            else:
                topic_arn = topic_name

            # Publish the message
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message_dict),
                MessageAttributes={
                    'ContentType': {
                        'DataType': 'String',
                        'StringValue': 'application/json'
                    }
                }
            )

            return {"messageId": response['MessageId']}
            
        except Exception as e:
            raise Exception(f"Failed to publish message to SNS topic {topic_name}: {str(e)}")
