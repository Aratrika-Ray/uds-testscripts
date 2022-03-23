import boto3
import logging
import uuid
from botocore.exceptions import ClientError
import os
import pandas

class instance:
    # Download asset from AWS S3 bucket'
    def downloadFileAWS(self, asset_id, folder):
        s3 = boto3.client('s3',self.s3Region)
        theFileData = s3.get_object(Bucket=self.s3Bucket, Key=asset_id)
        filenameHeader = "expected_"+theFileData['ContentDisposition']

        if(not os.path.exists(folder)):
            os.mkdir(folder)
        filePath = os.path.join(folder, filenameHeader)
        s3.download_file(self.s3Bucket, asset_id, filePath)

        #check if file is in .xlsx format
        if(filePath.endswith(".xls")):
            df = pandas.read_excel(filePath, header=None)
            df.to_excel(filePath.replace(".xls",".xlsx"), index=False, header=False)
            os.remove(filePath)
            filePath = filePath.replace(".xls", ".xlsx")
        
        return (theFileData, f"{filePath} downloaded")

    # Upload file to AWS S3 bucket
    def uploadFileAWS(self, file_name):
        # print("start upload")
        s3_client = boto3.client('s3',self.s3Region)
        logging.info("created client")
        asset_id = str(uuid.uuid1())
        # print("asset id: %s" %( asset_id))
        try:
            response = s3_client.upload_file(file_name, self.s3Bucket, asset_id, ExtraArgs={'ContentDisposition': os.path.basename(file_name).replace('original_', '')})
        except ClientError as e:    
            logging.error(e)
            return None
        return asset_id

    # constructor
    def __init__(self, s3Region, s3Bucket):
        self.s3Region = s3Region
        self.s3Bucket = s3Bucket

