#!/usr/bin/env python3
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
