import asyncio
import json
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

class GradingJob: 
    def __init__(self, email: str, checkpoint: int, url: str):
        self.email = email
        self.checkpoint = checkpoint
        self.url = url
    
    def __str__(self) -> str:
        return json.dumps({
            "email": self.email,
            "checkpoint": self.checkpoint,
            "url": self.url
        })

class MQ:
    def __init__(self, conn_str: str, queue_name: str):
        self.conn_str = conn_str
        self.queue_name = queue_name
    
    def send(self, grading_job: GradingJob) -> None:
        asyncio.run(self.send_messages([grading_job]))

    async def send_messages(self, grading_jobs: list[GradingJob]) -> None:
        async with ServiceBusClient.from_connection_string(
        conn_str=self.conn_str,
        logging_enable=True) as servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name=self.queue_name)
            async with sender:
                    messages = [ServiceBusMessage(str(job)) for job in grading_jobs]
                    await sender.send_messages(messages)
                    print("----Messages Sent ----")

import os
from dotenv import load_dotenv
async def main():
    load_dotenv()
    conn_str = os.get("SERVICE_BUS_CONNECTION_STRING")
    queue_name = os.get("SERVICE_BUS_QUEUE_NAME")
    mq = MQ(conn_str, queue_name)
    
    jobs = [
        GradingJob("user1@example.com", 1, "http://example.com/1"),
        GradingJob("user2@example.com", 2, "http://example.com/2"),
    ]
    
    await mq.send_messages(jobs)
    

if __name__ == "__main__":
    asyncio.run(main())