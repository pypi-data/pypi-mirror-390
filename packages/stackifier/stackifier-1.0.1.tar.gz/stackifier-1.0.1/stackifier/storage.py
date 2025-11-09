from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
import os

from .models import Event


class Writer(ABC):
    @abstractmethod
    def write(self, event: Event) -> None:
        pass
    
    @abstractmethod
    def flush(self) -> None:
        pass


class FileWriter(Writer):
    def __init__(self, path: str = "dataset/whatsapp_agent/convos.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._buffer = []
        self._buffer_size = 10
    
    def write(self, event: Event) -> None:
        self._buffer.append(event.to_json())
        if len(self._buffer) >= self._buffer_size:
            self.flush()
    
    def flush(self) -> None:
        if not self._buffer:
            return
        
        with open(self.path, "a", encoding="utf-8") as f:
            for line in self._buffer:
                f.write(line + "\n")
        self._buffer.clear()
    
    def __del__(self):
        try:
            self.flush()
        except:
            pass


class S3Writer(Writer):
    def __init__(
        self,
        bucket: str,
        key_template: str = "app/{env}/date={date}/conv_id={conv_id}/run_id={run_id}/log.jsonl",
        env: str = "dev",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1"
    ):
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for S3Writer. Install with: pip install boto3"
            )
        
        self.bucket = bucket
        self.key_template = key_template
        self.env = env
        
        session_kwargs = {"region_name": region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key
            })
        
        self.s3_client = boto3.client("s3", **session_kwargs)
        self._buffer = {}
    
    def _get_key(self, event: Event) -> str:
        date = datetime.fromisoformat(event.timestamp).strftime("%Y-%m-%d")
        return self.key_template.format(
            env=self.env,
            date=date,
            conv_id=event.conversation_id,
            run_id=event.run_id
        )
    
    def write(self, event: Event) -> None:
        key = self._get_key(event)
        if key not in self._buffer:
            self._buffer[key] = []
        self._buffer[key].append(event.to_json())
    
    def flush(self) -> None:
        if not self._buffer:
            return
        
        for key, lines in self._buffer.items():
            content = "\n".join(lines) + "\n"
            try:
                existing = self.s3_client.get_object(Bucket=self.bucket, Key=key)
                content = existing["Body"].read().decode("utf-8") + content
            except self.s3_client.exceptions.NoSuchKey:
                pass
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType="application/x-ndjson"
            )
        
        self._buffer.clear()
    
    def __del__(self):
        try:
            self.flush()
        except:
            pass
