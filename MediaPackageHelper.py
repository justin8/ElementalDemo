import time
from pprint import pprint
from contextlib import suppress

import boto3
import botocore

# Python Modules with a series of useful helper methods
# for dealing with Elemental MediaPackage using BOTO3

# Underlying assumption is that this module will manipulate resources
# with the specified 'tag_name':'tag_value' tags


class MediaPackageHelper:
    def __init__(self, resource_prefix, tags,):
        self.client = boto3.client('mediapackage')
        self.channel_id = f"{resource_prefix}_package_channel"
        self.origin_endpoint_id = f"{resource_prefix}_package_origin_endpoint"
        self.resource_prefix = resource_prefix
        self.tags = tags

    def create(self):
        self._create_channel()
        self._create_hls_endpoint()

    def _create_channel(self):
        self.client.create_channel(
            Id=self.channel_id,
            Tags=self.tags,
        )
        print(f"Created MediaPackage channel '{self.channel_id}'")

    def _create_hls_endpoint(self):
        response = self.client.create_origin_endpoint(
            ChannelId=self.channel_id,
            Id=self.origin_endpoint_id,
            HlsPackage={
                'PlaylistType': 'EVENT',
                'PlaylistWindowSeconds': 300,
                'ProgramDateTimeIntervalSeconds': 60,
                'SegmentDurationSeconds': 4
            },
            Tags=self.tags)
        self.origin_url = response["Url"]
        print(f"Created HLS origin endpoint with ID: {self.origin_endpoint_id}")

    def cleanup(self):
        with suppress(Exception):
            self.cleanup_origin_endpoints()
        with suppress(Exception):
            self.cleanup_channels()

    def cleanup_origin_endpoints(self):
        response = self.client.list_origin_endpoints()

        for endpoint in self.filter_by_tags(response['OriginEndpoints']):
            try:
                print(f"Deleting Origin Endpoint with ID: {endpoint['Id']}")
                response = self.client.delete_origin_endpoint(Id=endpoint['Id'])
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Code'])
                pprint(e)

    def cleanup_channels(self):
        response = self.client.list_channels()

        for endpoint in self.filter_by_tags(response['Channels']):
            try:
                print(f"Deleting Origin Endpoint with ID: {endpoint['Id']}")
                response = self.client.delete_channel(Id=endpoint['Id'])
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Code'])
                pprint(e)

    def filter_by_tags(self, items):
        return [x for x in items if "project" in x["Tags"] and x["Tags"]["project"] == self.tags["project"]]
