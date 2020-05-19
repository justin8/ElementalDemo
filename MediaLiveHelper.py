import sys
import time
from pprint import pprint
import random
import math
import functools
from contextlib import suppress

import boto3
import botocore

# Python Modules with a series of useful helper methods
# for dealing with Elemental MediaLive using BOTO3

# Underlying assumption is that this module will manipulate resources
# with the specified 'tag_name':'tag_value' tags


class MediaLiveHelper:
    def __init__(self, security_cidr, media_package_channel_id, resource_prefix, tags):
        self.client = boto3.client('medialive')
        self.channel_id = None
        self.security_cidr = security_cidr
        self.resource_prefix = resource_prefix
        self.media_package_channel_id = media_package_channel_id
        self.tags = tags
        self.waitTime = 2

    def create(self):
        self._create_input_security_group()
        self._create_rtmp_input()
        self._create_channel()

    def _create_input_security_group(self):
        response = self.client.create_input_security_group(
            Tags=self.tags,
            WhitelistRules=[{"Cidr": self.security_cidr}]
        )
        self.security_group_id = response["SecurityGroup"]["Id"]
        print(f"Created Input Security Group with ID: {self.security_group_id}")

    def _create_rtmp_input(self):
        response = self.client.create_input(
            Name=f"{self.resource_prefix}_rtmp_push_input",
            RoleArn=self.get_medialive_role_arn,
            Type="RTMP_PUSH",
            InputSecurityGroups=[self.security_group_id],
            Destinations=[{"StreamName": "live"}],
            Tags=self.tags,
        )
        self.input_id = response["Input"]["Id"]
        self.input_destinations = response["Input"]["Destinations"]
        print(f"Created RTMP Input with ID: {self.input_id}")

    def _create_channel(self):
        destination_id = str(math.floor(time.time()))
        response = self.client.create_channel(
            ChannelClass="SINGLE_PIPELINE",
            Destinations=[{
                "Id": destination_id,
                "MediaPackageSettings": [{"ChannelId": self.media_package_channel_id}]
            }],
            EncoderSettings=self._encoder_settings(destination_id),
            InputAttachments=self._input_attachments(),
            InputSpecification={
                "Codec": "AVC",
                "MaximumBitrate": "MAX_20_MBPS",
                "Resolution": "HD",
            },
            LogLevel="DEBUG",
            Name=f"{self.resource_prefix}_channel",
            RoleArn=self.get_medialive_role_arn,
            Tags=self.tags,
        )
        self.channel_id = response["Channel"]["Id"]

    def _encoder_settings(self, destination_id):
        return {
            "AudioDescriptions": [{
                "AudioSelectorName": f"{self.resource_prefix}_audio",
                "AudioTypeControl": "FOLLOW_INPUT",
                "CodecSettings": {
                    "AacSettings": {
                        "Bitrate": 192000,
                        "CodingMode": "CODING_MODE_2_0",
                        "InputType": "NORMAL",
                        "Profile": "LC",
                        "RateControlMode": "CBR",
                        "RawFormat": "NONE",
                        "SampleRate": 48000,
                        "Spec": "MPEG4"
                    }
                },
                "LanguageCodeControl": "FOLLOW_INPUT",
                "Name": "audio"
            }],
            "OutputGroups": [{
                "Name": "emp_output",
                "OutputGroupSettings": {
                        "MediaPackageGroupSettings": {
                            "Destination": {
                                "DestinationRefId": destination_id
                            }
                        }
                },
                "Outputs": [
                    {
                        "AudioDescriptionNames": [],
                        "CaptionDescriptionNames": [],
                        "OutputName": "video_4mpbs",
                        "OutputSettings": {
                            "MediaPackageOutputSettings": {}
                        },
                        "VideoDescriptionName": "video_4mpbs"
                    },
                    {
                        "AudioDescriptionNames": [],
                        "CaptionDescriptionNames": [],
                        "OutputName": "video_2mpbs",
                        "OutputSettings": {
                            "MediaPackageOutputSettings": {}
                        },
                        "VideoDescriptionName": "video_2mpbs"
                    },
                    {
                        "AudioDescriptionNames": [],
                        "CaptionDescriptionNames": [],
                        "OutputName": "video_1_2mpbs",
                        "OutputSettings": {
                            "MediaPackageOutputSettings": {}
                        },
                        "VideoDescriptionName": "video_1_2mpbs"
                    },
                    {
                        "AudioDescriptionNames": [
                            "audio"
                        ],
                        "CaptionDescriptionNames": [],
                        "OutputName": "audio",
                        "OutputSettings": {
                            "MediaPackageOutputSettings": {}
                        }
                    }
                ]
            }],
            "TimecodeConfig": {
                "Source": "EMBEDDED"
            },
            "VideoDescriptions": [{
                "Name": "video_4mpbs",
                "Width": 1920,
                "Height": 1080,
                "RespondToAfd": "NONE",
                "ScalingBehavior": "DEFAULT",
                "Sharpness": 50,
                "CodecSettings": {
                        "H264Settings": {
                            "AdaptiveQuantization": "HIGH",
                            "AfdSignaling": "NONE",
                            "Bitrate": 4000000,
                            "BufFillPct": 90,
                            "BufSize": 8000000,
                            "ColorMetadata": "INSERT",
                            "EntropyEncoding": "CABAC",
                            "FlickerAq": "DISABLED",
                            "FramerateControl": "SPECIFIED",
                            "FramerateDenominator": 1,
                            "FramerateNumerator": 50,
                            "GopBReference": "DISABLED",
                            "GopClosedCadence": 1,
                            "GopNumBFrames": 3,
                            "GopSize": 2,
                            "GopSizeUnits": "SECONDS",
                            "Level": "H264_LEVEL_AUTO",
                            "LookAheadRateControl": "HIGH",
                            "MaxBitrate": 6000000,
                            "NumRefFrames": 3,
                            "ParControl": "SPECIFIED",
                            "ParDenominator": 1,
                            "ParNumerator": 1,
                            "Profile": "HIGH",
                            "QvbrQualityLevel": 9,
                            "RateControlMode": "QVBR",
                            "ScanType": "PROGRESSIVE",
                            "SceneChangeDetect": "ENABLED",
                            "Slices": 4,
                            "SpatialAq": "ENABLED",
                            "SubgopLength": "FIXED",
                            "Syntax": "DEFAULT",
                            "TemporalAq": "DISABLED",
                            "TimecodeInsertion": "DISABLED"
                        }
                },
            },
                {
                "Name": "video_2mpbs",
                    "Width": 1280,
                    "Height": 720,
                    "RespondToAfd": "NONE",
                    "ScalingBehavior": "DEFAULT",
                    "Sharpness": 50,
                    "CodecSettings": {
                        "H264Settings": {
                            "AdaptiveQuantization": "HIGH",
                            "AfdSignaling": "NONE",
                            "Bitrate": 2000000,
                            "BufFillPct": 90,
                            "BufSize": 4000000,
                            "ColorMetadata": "INSERT",
                            "EntropyEncoding": "CABAC",
                            "FlickerAq": "DISABLED",
                            "FramerateControl": "SPECIFIED",
                            "FramerateDenominator": 1,
                            "FramerateNumerator": 50,
                            "GopBReference": "DISABLED",
                            "GopClosedCadence": 1,
                            "GopNumBFrames": 3,
                            "GopSize": 2,
                            "GopSizeUnits": "SECONDS",
                            "Level": "H264_LEVEL_AUTO",
                            "LookAheadRateControl": "HIGH",
                            "MaxBitrate": 3000000,
                            "NumRefFrames": 3,
                            "ParControl": "SPECIFIED",
                            "ParDenominator": 1,
                            "ParNumerator": 1,
                            "Profile": "HIGH",
                            "QvbrQualityLevel": 9,
                            "RateControlMode": "QVBR",
                            "ScanType": "PROGRESSIVE",
                            "SceneChangeDetect": "ENABLED",
                            "Slices": 2,
                            "SpatialAq": "ENABLED",
                            "SubgopLength": "FIXED",
                            "Syntax": "DEFAULT",
                            "TemporalAq": "DISABLED",
                            "TimecodeInsertion": "DISABLED"
                        }
                    },
            },
                {
                "Name": "video_1_2mpbs",
                    "Width": 1024,
                    "Height": 576,
                    "RespondToAfd": "NONE",
                    "ScalingBehavior": "DEFAULT",
                    "Sharpness": 50,
                    "CodecSettings": {
                        "H264Settings": {
                            "AdaptiveQuantization": "HIGH",
                            "AfdSignaling": "NONE",
                            "Bitrate": 1200000,
                            "BufFillPct": 90,
                            "BufSize": 2400000,
                            "ColorMetadata": "INSERT",
                            "EntropyEncoding": "CABAC",
                            "FlickerAq": "DISABLED",
                            "FramerateControl": "SPECIFIED",
                            "FramerateDenominator": 1,
                            "FramerateNumerator": 50,
                            "GopBReference": "DISABLED",
                            "GopClosedCadence": 1,
                            "GopNumBFrames": 3,
                            "GopSize": 2,
                            "GopSizeUnits": "SECONDS",
                            "Level": "H264_LEVEL_AUTO",
                            "LookAheadRateControl": "HIGH",
                            "MaxBitrate": 1800000,
                            "NumRefFrames": 3,
                            "ParControl": "SPECIFIED",
                            "ParDenominator": 1,
                            "ParNumerator": 1,
                            "Profile": "MAIN",
                            "QvbrQualityLevel": 7,
                            "RateControlMode": "QVBR",
                            "ScanType": "PROGRESSIVE",
                            "SceneChangeDetect": "ENABLED",
                            "Slices": 1,
                            "SpatialAq": "ENABLED",
                            "SubgopLength": "FIXED",
                            "Syntax": "DEFAULT",
                            "TemporalAq": "DISABLED",
                            "TimecodeInsertion": "DISABLED"
                        }
                    },
            }]
        }

    def _input_attachments(self):
        return [{
                "InputAttachmentName": "elemental_rtmp_push_input",
                "InputId": self.input_id,
                "InputSettings": {
                    "AudioSelectors": [],
                    "CaptionSelectors": [],
                    "DeblockFilter": "DISABLED",
                    "DenoiseFilter": "DISABLED",
                    "FilterStrength": 1,
                    "InputFilter": "AUTO",
                    "SourceEndBehavior": "CONTINUE"
                }
                }]

    @functools.cached_property
    def get_medialive_role_arn(self):
        iam = boto3.client("iam")
        try:
            response = iam.get_role(RoleName="MediaLiveAccessRole")
            return response["Role"]["Arn"]
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                print("Cannot find the MediaLiveAccessRole. Please open the Elemental MediaLive console in your account and follow the steps to create the service role")
                print(
                    "From the console, click 'Create Channel' -> 'Create role from template' -> 'Create IAM Role'")
                print("Or follow this doc for more instructions: https://docs.aws.amazon.com/medialive/latest/ug/scenarios-for-medialive-role.html")
                sys.exit(1)

    def start_channel(self):
        channel_id = self.get_channel_id()
        channelRunning = False
        while not channelRunning:
            response = self.client.describe_channel(ChannelId=channel_id)
            state = response['State']
            if state == "IDLE":
                try:
                    print(f"Starting Channel with ID: {channel_id}")
                    response = self.client.start_channel(ChannelId=channel_id)
                except botocore.exceptions.ClientError as e:
                    print(e.response['Error']['Code'])
                    pprint(e)
            elif state == "CREATING" or state == "UPDATING":
                print(f"Channel still CREATING/UPDATING, wait {self.waitTime} seconds ...")
                time.sleep(self.waitTime)
            elif state == "STARTING":
                print(f"Channel {channel_id} starting")
                channelRunning = True
            else:
                print(f"Unknown condition STATE[{state}]")

    def stop_channel(self):
        channel_id = self.get_channel_id()
        channelRunning = True
        while channelRunning:
            response = self.client.describe_channel(ChannelId=channel_id)
            state = response['State']
            if state == "RUNNING":
                print(f"Stopping channel {channel_id}")
                self.client.stop_channel(ChannelId=channel_id)
            elif state == "STOPPING" or state == "STARTING":
                print(f"Channel still 'stopping', waiting {self.waitTime} seconds ...")
                time.sleep(self.waitTime)
            elif state == "IDLE":
                print("Channel " + channel_id + " has stopped")
                channelRunning = False
            else:
                print(f"Unknown condition STATE[{state}]")

    def get_channel_id(self):
        if self.channel_id:
            return self.channel_id
        try:
            response = self.client.list_channels()
        except botocore.exceptions.ClientError as e:
            print(e.response['Error']['Code'])
        for channel in self.filter_by_tags(response['Channels']):
            self.channel_id = channel['Id']
        if not self.channel_id:
            raise RuntimeError("Unable to determine specified channel ID")
        return self.channel_id

    def cleanup(self):
        with suppress(Exception):
            self.stop_channel()
        with suppress(Exception):
            self.cleanup_channels()
        with suppress(Exception):
            self.cleanup_inputs()
        with suppress(Exception):
            self.cleanup_input_security_group()

    def cleanup_input_security_group(self):
        response = self.client.list_input_security_groups()

        for security_group in self.filter_by_tags(response['InputSecurityGroups']):
            try:
                print(f"Deleting Input Security Group with ID: {security_group['Id']}")
                response = self.client.delete_input_security_group(InputSecurityGroupId=security_group['Id'])
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Code'])
                pprint(e)

    def cleanup_inputs(self):
        response = self.client.list_inputs()
        for input in self.filter_by_tags(response['Inputs']):
            try:
                print(f"Deleting Input with ID: {input['Id']}")
                response = self.client.delete_input(InputId=input['Id'])
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Code'])
                pprint(e)

    def cleanup_channels(self):
        response = self.client.list_channels()
        for channel in self.filter_by_tags(response['Channels']):
            channel_id = channel['Id']
            try:
                print(f"Deleting Channel with ID: {channel['Id']}")
                response = self.client.delete_channel(ChannelId=channel_id)
            except botocore.exceptions.ClientError as e:
                print(e.response['Error']['Code'])

            deletingChannel = True
            while deletingChannel == True:
                # Check channel state
                response = self.client.describe_channel(
                    ChannelId=channel_id)
                state = response['State']
                if state == "DELETING":
                    print(f"Wait {self.waitTime} seconds for channel to be deleted")
                    time.sleep(self.waitTime)
                elif state == "DELETED":
                    print("Channel " + channel_id + " has been deleted")
                    deletingChannel = False
                else:
                    print("Unknown condition STATE[" + state + "]")
                    pprint(response)

    def filter_by_tags(self, items):
        return [x for x in items if "project" in x["Tags"] and x["Tags"]["project"] == self.tags["project"]]
