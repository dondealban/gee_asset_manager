#! /usr/bin/env python

import argparse
import logging
import os
import ee

from gee_asset_manager.batch_remover import delete
from gee_asset_manager.batch_uploader import upload
from gee_asset_manager.config import setup_logging


def cancel_all_running_tasks():
    logging.info('Attempting to cancel all running tasks')
    running_tasks = [task for task in ee.data.getTaskList() if task['state'] == 'RUNNING']
    for task in running_tasks:
        ee.data.cancelTask(task['id'])
    logging.info('Cancel all request completed')


def cancel_all_running_tasks_from_parser(args):
    cancel_all_running_tasks()
    

def delete_collection_from_parser(args):
    delete(args.id)


def upload_from_parser(args):
    upload(user=args.user,
           source_path=args.source,
           destination_path=args.dest,
           metadata_path=args.metadata,
           multipart_upload=args.large,
           nodata_value=args.nodata,
           bucket_name=args.bucket)


def main(args=None):
    setup_logging()
    parser = argparse.ArgumentParser(description='Google Earth Engine Batch Asset Manager')

    subparsers = parser.add_subparsers()
    parser_delete = subparsers.add_parser('delete', help='Deletes collection and all items inside. Supports Unix-like wildcards.')
    parser_delete.add_argument('id', help='Full path to asset for deletion. Recursively removes all folders, collections and images.')
    parser_delete.set_defaults(func=delete_collection_from_parser)
    parser_delete.add_argument('-s', '--service-account', help='Google Earth Engine service account.')
    parser_delete.add_argument('-k', '--private-key', help='Google Earth Engine private key file.')

    parser_upload = subparsers.add_parser('upload', help='Batch Asset Uploader.')
    required_named = parser_upload.add_argument_group('Required named arguments.')
    required_named.add_argument('--source', help='Path to the directory with images for upload.', required=True)
    required_named.add_argument('--dest', help='Destination. Full path for upload to Google Earth Engine, e.g. users/pinkiepie/myponycollection', required=True)
    optional_named = parser_upload.add_argument_group('Optional named arguments')
    optional_named.add_argument('-m', '--metadata', help='Path to CSV with metadata.')
    optional_named.add_argument('--large', action='store_true', help='(Advanced) Use multipart upload. Might help if upload of large '
                                                                     'files is failing on some systems. Might cause other issues.')
    optional_named.add_argument('--nodata', type=int, help='The value to burn into the raster as NoData (missing data)')

    required_named.add_argument('-u', '--user', help='Google account name (gmail address).')
    optional_named.add_argument('-s', '--service-account', help='Google Earth Engine service account.')
    optional_named.add_argument('-k', '--private-key', help='Google Earth Engine private key file.')
    optional_named.add_argument('-b', '--bucket', help='Google Cloud Storage bucket name.')

    parser_upload.set_defaults(func=upload_from_parser)

    parser_cancel = subparsers.add_parser('cancel', help='Cancel all running tasks')
    parser_cancel.set_defaults(func=cancel_all_running_tasks_from_parser)
    parser_cancel.add_argument('-s', '--service-account', help='Google Earth Engine service account.')
    parser_cancel.add_argument('-k', '--private-key', help='Google Earth Engine private key file.')

    args = parser.parse_args()

    if args.service_account:
        credentials = ee.ServiceAccountCredentials(args.service_account, args.private_key)
        ee.Initialize(credentials)
    else:
        ee.Initialize()

    if args.private_key is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.private_key

    args.func(args)

if __name__ == '__main__':
    main()