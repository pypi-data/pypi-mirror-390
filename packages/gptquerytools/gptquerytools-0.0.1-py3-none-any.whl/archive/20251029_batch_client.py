# gptquery/core/batch_client.py
# Archived becuase no longer planning to implement.
##################################################

import json
import time
import os
from openai import OpenAI

class OpenAIBatchClient:
    """
    A client for interacting with the OpenAI Batch API.

    This client handles the creation of batch files, uploading,
    job submission, status checking, and results retrieval.
    """
    def __init__(self, api_key: str = None): # type: ignore
        """
        Initializes the OpenAI client.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def create_jsonl_file(self, prompts: list[dict], file_path: str = "batch_input.jsonl") -> str:
        """
        Creates a JSONL file from a list of prompts in the format required by the Batch API.

        Args:
            prompts (list[dict]): A list of dictionaries, where each dict contains
                                 the parameters for a single API call (e.g., model, messages).
            file_path (str): The path to save the JSONL file.

        Returns:
            str: The path to the created JSONL file.
        """
        with open(file_path, 'w') as f:
            for i, prompt in enumerate(prompts):
                json_record = {
                    "custom_id": f"request-{i+1}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": prompt
                }
                f.write(json.dumps(json_record) + '\\n')
        return file_path

    def upload_file(self, file_path: str) -> str:
        """
        Uploads a file to OpenAI for batch processing.

        Args:
            file_path (str): The path to the JSONL file.

        Returns:
            str: The ID of the uploaded file.
        """
        with open(file_path, "rb") as f:
            batch_input_file = self.client.files.create(
                file=f,
                purpose="batch"
            )
        return batch_input_file.id

    def submit_batch_job(self, file_id: str) -> str:
        """
        Submits a batch job to OpenAI.

        Args:
            file_id (str): The ID of the uploaded file.

        Returns:
            str: The ID of the created batch job.
        """
        batch_job = self.client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        return batch_job.id

    def check_batch_status(self, batch_id: str) -> dict:
        """
        Retrieves the status of a batch job.

        Args:
            batch_id (str): The ID of the batch job.

        Returns:
            dict: The batch object with the current status.
        """
        return self.client.batches.retrieve(batch_id)

    def get_batch_results(self, batch_job: dict) -> list[dict]:
        """
        Downloads and reads the results from a completed batch job.

        Args:
            batch_job (dict): The completed batch job object.

        Returns:
            list[dict]: A list of result objects from the batch processing.
        """
        if batch_job.status != 'completed':
            raise ValueError(f"Batch job {batch_job.id} is not yet completed. Current status: {batch_job.status}")

        output_file_id = batch_job.output_file_id
        if not output_file_id:
            return []

        file_content = self.client.files.content(output_file_id).read()
        
        results = []
        for line in file_content.strip().split(b'\\n'):
            results.append(json.loads(line))
            
        return results

    def wait_for_completion(self, batch_id: str, poll_interval: int = 30) -> dict:
        """
        Waits for a batch job to complete, polling at a specified interval.

        Args:
            batch_id (str): The ID of the batch job.
            poll_interval (int): The time in seconds between status checks.

        Returns:
            dict: The completed batch object.
        """
        while True:
            batch_job = self.check_batch_status(batch_id)
            if batch_job.status == 'completed':
                print(f"Batch job {batch_id} completed.")
                break
            elif batch_job.status in ['failed', 'expired', 'cancelled']:
                raise RuntimeError(f"Batch job {batch_id} failed with status: {batch_job.status}")
            
            print(f"Batch job {batch_id} is still in progress (status: {batch_job.status}). Waiting...")
            time.sleep(poll_interval)
            
        return batch_job
