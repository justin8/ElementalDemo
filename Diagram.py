#!/usr/bin/env python3
from diagrams.aws.network import CloudFront
import diagrams
from diagrams import Cluster, Diagram
from diagrams.aws.media import ElementalMedialive, ElementalMediapackage
from diagrams.onprem.client import Users, Client

with Diagram("", filename="demo-diagram", show=False):
    video_source = Client("Video Source")
    live = ElementalMedialive("AWS Elemental\nMediaLive Channel")
    package = ElementalMediapackage("AWS Elemental\nMediaPackage Channel")
    viewers = Users("Viewers")

    video_source >> live >> package >> viewers

with Diagram("", filename="production-diagram", show=True):
    video_source = Client("Video Source")
    viewers = Users("Viewers")
    cloudfront = CloudFront("Amazon CloudFront\n(Content Delivery Network)")

    with Cluster("AWS Elemental\nMediaLive Channel"):
        live1 = ElementalMedialive("Ingestion pipeline 1")
        live2 = ElementalMedialive("Ingestion pipeline 2")

    with Cluster("AWS Elemental\nMediaPackage Channel"):
        package1 = ElementalMediapackage("Packaging pipeline 1")
        package2 = ElementalMediapackage("Packaging pipeline 2")

    video_source >> live1 >> package1 >> cloudfront
    video_source >> live2 >> package2 >> cloudfront
    cloudfront >> viewers
