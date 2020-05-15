#!/usr/bin/env python3

import sys
import boto3
import botocore
import click

import MediaLiveHelper
import MediaPackageHelper


@click.command()
@click.option("--pipeline-name", default="elementalTest", help="Resources created will be tagged as project:$pipeline-name")
@click.option("--security-cidr", default="0.0.0.0/0", help="Specify a CIDR range that is allowed to send traffic to the RTMP endpoint")
@click.option("--cleanup", is_flag=True, help="Cleanup the resources created by this script based on the given pipeline-name")
def main(pipeline_name, security_cidr, cleanup):
    tags = {"project": pipeline_name}

    media_package_helper = MediaPackageHelper.MediaPackageHelper(
        resource_prefix=pipeline_name,
        tags=tags)
    media_live_helper = MediaLiveHelper.MediaLiveHelper(
        security_cidr=security_cidr,
        media_package_channel_id=media_package_helper.channel_id,
        resource_prefix=pipeline_name,
        tags=tags)

    if cleanup:
        print("Beginning cleanup...")
        media_live_helper.cleanup()
        media_package_helper.cleanup()
        print("Cleanup successful!")
    else:
        media_package_helper.create()
        media_live_helper.create()
        media_live_helper.start_channel()

        print()
        print(f"MediaPackage HLS Endpoint URL: {media_package_helper.origin_url}")
        print("MediaLive Input Paramaters")
        destination = media_live_helper.input_destinations[0]
        for k, v in destination.items():
            print(f"\t {k}: {v}")


if __name__ == "__main__":
    main()
