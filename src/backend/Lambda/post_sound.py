import json
import sys
import os
import logging

# 同じディレクトリにpip installしたpackagesを参照
sys.path.append(os.path.join(os.path.dirname(__file__), '../packages'))
from packages import boto3
from packages.botocore.exceptions import ClientError
from packages.botocore.client import Config

def createResponse(statusCode, header, body, isBase64Encoded=False):
    response = {
        "isBase64Encoded": isBase64Encoded,
        "statusCode": statusCode,
        "headers": header,
        "body": json.dumps(body)
    }
    return response

s3 = boto3.client('s3', 'ap-northeast-1', config=Config(signature_version='s3v4'))
bucket_name = os.environ['bucket_name']

def regist_info(body):
    # 入力された情報をパース、DBに格納
    # 現状仮でTrueを返すのみ
    return True

def handler(event, context):
    query = event['queryStringParameters']
    body = event['body']

    # 拡張子設定(デフォルトはmp3)
    ext = 'mp3'
    if 'extension' in query:
        ext = query['extension']

    is_regist_success = regist_info(body)

    # 情報の格納が完了したら、S3署名付きURLを発行する
    if is_regist_success:
        try:
            upload_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket':bucket_name,
                    'Key': 'raw/{}.{}'.format(query['name'], ext)
                },
                ExpiresIn=300, #5分
                HttpMethod='PUT'
            )
            logging.info(upload_url)
            res = {
                'message': 'success',
                'upload_url': upload_url
            }
            return createResponse(201, {}, res)
        except ClientError as e:
            logging.error(e)
            return createResponse(500, {}, {'message': 'Internal server error'})
    