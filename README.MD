# AWS Elemental Demo

The script here is designed to spin up an example AWS Elemental MediaLive and MediaPackage pipeline to publish a live video stream out to a HLS endpoint in a fully serverless manner.

## Requirements

- Python 3.8+
- An RTMP streaming app for your phone (e.g. Zixi OnAir)

## Usage

1. Run `pip install -r requirements.txt` to install the dependencies
2. Run `./DemoPipeline.py` to create a pipeline
3. Copy+paste the m3u8 link for the HLS stream to your browser (Safari works out of the box, others may vary)
   1. Alternatively you can open the MediaPackage console, open the endpoint and click preview in that view
4. Input the RTMP stream values in to a streaming app on your phone or other device. Typically you will put the `/live` in the stream field, and the IP address in the server field of your application
5. When you're finished, run `./DemoPipeline.py --cleanup` to delete all of the resources
