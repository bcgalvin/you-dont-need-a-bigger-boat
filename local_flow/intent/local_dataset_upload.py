"""

Upload local .csv dataset as .parquet in S3

"""
from dotenv import load_dotenv
load_dotenv('.env')

import os
from typing import Optional, List

import pandas as pd
from metaflow.metaflow_config import DATATOOLS_S3ROOT

from src.utils import get_filename


def upload_file_as_parquet(file_path: str,
                           target_s3_folder: str,
                           chunksize: Optional[int] = None,
                           partition_cols: Optional[List[str]] = None) -> None:
    print(f'Begin reading file {file_path}')

    s3_file_name = os.path.join(
        target_s3_folder, get_filename(file_path) + '.parquet')
    if chunksize is not None:
        df_content = next(pd.read_csv(file_path, chunksize=chunksize))
    else:
        df_content = pd.read_csv(file_path)

    print('Begin upload to S3')
    df_content.to_parquet(path=s3_file_name, engine='pyarrow',
                          partition_cols=partition_cols)

    print(f'Parquet files for {file_path} stored at : {s3_file_name}')


if __name__ == '__main__':
    SKU_TO_CONTENT_PATH = os.getenv('SKU_TO_CONTENT_PATH')
    BROWSING_TRAIN_PATH = os.getenv('BROWSING_TRAIN_PATH')
    SEARCH_TRAIN_PATH = os.getenv('SEARCH_TRAIN_PATH')
    PARQUET_S3_PATH = os.getenv('PARQUET_S3_PATH')
    TARGET_S3_PATH = os.path.join(DATATOOLS_S3ROOT, PARQUET_S3_PATH)

    # upload to S3 at some know path under the CartFlow directory
    # for now, upload some rows
    # there is no versioning whatsoever at this stage
    upload_file_as_parquet(SKU_TO_CONTENT_PATH, TARGET_S3_PATH)
    upload_file_as_parquet(BROWSING_TRAIN_PATH, TARGET_S3_PATH)
    upload_file_as_parquet(SEARCH_TRAIN_PATH, TARGET_S3_PATH)
