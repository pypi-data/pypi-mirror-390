import boto3
import os
from datetime import datetime, UTC, timedelta
from typing import List
from inception_helper_func.common_validator import AttachmentDType
import traceback
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # S3 Settings
    s3_access_key: str = None
    s3_secret_key: str = None
    s3_bucket_name: str = None
    s3_region_name: str = None
    s3_bucket_name_thumbnail: str = None
    s3_region_name_thumbnail: str = None

    env_file: str = os.path.join(os.path.dirname(__file__), "/app/config.env")
    load_dotenv(dotenv_path=env_file)
    model_config = SettingsConfigDict(env_file=env_file)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_s3_client(region_name: str = None):
    if not all(
        [settings.s3_access_key, settings.s3_secret_key, settings.s3_region_name]
    ):
        raise ValueError(
            "S3 configuration is incomplete. Please check s3_access_key, s3_secret_key, and s3_region_name settings."
        )

    return boto3.client(
        "s3",
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=region_name if region_name else settings.s3_region_name,
    )


def download_file_from_s3(key: str):
    if not settings.s3_bucket_name:
        raise ValueError("S3 bucket name is not configured.")

    s3 = get_s3_client()
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": key},
        ExpiresIn=3600,
    )
    return url


def get_list_of_s3_presigned_url(attachments: List[AttachmentDType] = []):
    if not settings.s3_bucket_name:
        raise ValueError("S3 bucket name is not configured.")

    try:
        s3 = get_s3_client()
        expires_in = 3600 * 24
        created_at = datetime.now(UTC)
        created_at_epoch = int(created_at.timestamp())
        created_at_iso = created_at.isoformat()
        expires_at = created_at + timedelta(seconds=expires_in)
        expires_at_epoch = int(expires_at.timestamp())
        expires_at_iso = expires_at.isoformat()
        atts = []

        for attachment in attachments:
            try:
                url = s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.s3_bucket_name,
                        "Key": attachment["key"],
                    },
                    ExpiresIn=expires_in,
                )

                attachment["url"] = url
                attachment["created_at_epoch"] = created_at_epoch
                attachment["created_at_iso"] = created_at_iso
                attachment["expires_at_epoch"] = expires_at_epoch
                attachment["expires_at_iso"] = expires_at_iso
                atts.append(attachment)
            except Exception as e:
                print(
                    f"Error generating presigned URL for key {attachment['key']}: {str(e)}"
                )
                # Add attachment without URL for failed ones
                attachment["url"] = ""
                attachment["error"] = str(e)
                atts.append(attachment)

        return atts
    except Exception as e:
        print(f"Error in get_list_of_s3_presigned_url: {str(traceback.format_exc())}")
        return []
