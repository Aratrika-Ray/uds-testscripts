<<<<<<< HEAD
import boto3
import logging
import uuid
from botocore.exceptions import ClientError
import os
import pandas

class instance:
    # Download asset from AWS S3 bucket
    def downloadFileAWS(self, asset_id, folder):
        s3 = boto3.client('s3',self.s3Region)
        # print("asset id to download:" + asset_id)
        theFileData = s3.get_object(Bucket=self.s3Bucket, Key=asset_id)
        print("file meta data: %s\n" %( theFileData))
        filenameHeader = theFileData["ContentDisposition"]
        # print("filename after split %s" %(filenameHeader))

        # create unit test folder
        if(not os.path.exists(folder)):
            os.mkdir(folder)
            print(f"{folder} created")
        filePath = os.path.join(folder, filenameHeader)
        print(f"\n{filePath}\n")

        s3.download_file(self.s3Bucket, asset_id, filePath)
        print("done download")

        #check if file is in .xlsx format
        if(filePath.endswith(".xls")):
            df = pandas.read_excel(filePath, header=None)
            df.to_excel(filePath.replace(".xls",".xlsx"), index=False, header=False)
            os.remove(filePath)

        return filePath

    # Upload file to AWS S3 bucket
    def uploadFileAWS(self, file_name):
        print("start upload")
        s3_client = boto3.client('s3',self.s3Region)
        logging.info("created client")
        asset_id = str(uuid.uuid1())
        print("asset id: %s" %( asset_id))
        try:
            response = s3_client.upload_file(file_name, self.s3Bucket, asset_id,ExtraArgs={'ContentDisposition': str(os.path.basename(file_name))})
        except ClientError as e:
            logging.error(e)
            return None
        return asset_id

    # constructor
    def __init__(self, s3Region, s3Bucket):
        self.s3Region = s3Region
        self.s3Bucket = s3Bucket
=======
import boto3
import logging
import uuid
from botocore.exceptions import ClientError
import os
import pandas

class instance:
    # Download asset from AWS S3 bucket
    def downloadFileAWS(self, asset_id, folder):
        s3 = boto3.client('s3',self.s3Region)
        # print("asset id to download:" + asset_id)
        theFileData = s3.get_object(Bucket=self.s3Bucket, Key=asset_id)
        print("file meta data: %s\n" %( theFileData))
        filenameHeader = theFileData["ContentDisposition"]
        # print("filename after split %s" %(filenameHeader))

        # create unit test folder
        if(not os.path.exists(folder)):
            os.mkdir(folder)
            print(f"{folder} created")
        filePath = os.path.join(folder, filenameHeader)
        print(f"\n{filePath}\n")

        s3.download_file(self.s3Bucket, asset_id, filePath)
        print("done download")

        #check if file is in .xlsx format
        if(filePath.endswith(".xls")):
            df = pandas.read_excel(filePath, header=None)
            df.to_excel(filePath.replace(".xls",".xlsx"), index=False, header=False)
            os.remove(filePath)

        return filePath

    # Upload file to AWS S3 bucket
    def uploadFileAWS(self, file_name):
        print("start upload")
        s3_client = boto3.client('s3',self.s3Region)
        logging.info("created client")
        asset_id = str(uuid.uuid1())
        print("asset id: %s" %( asset_id))
        try:
            response = s3_client.upload_file(file_name, self.s3Bucket, asset_id,ExtraArgs={'ContentDisposition': str(file_name)})
        except ClientError as e:
            logging.error(e)
            return None
        return asset_id

    # constructor
    def __init__(self, s3Region, s3Bucket):
        self.s3Region = s3Region
        self.s3Bucket = s3Bucket
>>>>>>> ca021bb0b21902343875533183cdf1725fcf2ea6
