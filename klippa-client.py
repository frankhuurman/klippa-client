#!/usr/bin/env python3

import aiofiles
import aiohttp
import asyncio
import json
import os
import requests
import sys
import time

from base64 import b64encode
from config.config_client import ConfigClient
from dirwatcher import DirectoryWatcher
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class Main():

    # Constants
    TEST_API_URL = "http://127.0.0.1:5000/test"
    API_URL = "https://custom-ocr.klippa.com/api/v1/parseDocument"
    ARGS = None

    # file validation
    VALID_TYPES = {"gif", "heic", "heif", "jpg", "jpeg", "pdf", "png",
                    "GIF", "HEIC", "HEIF", "JPG", "JPEG","PDF", "PNG"}

    def create_observer(self, args):

        dirwatcher = DirectoryWatcher()
        event_handler = dirwatcher.create_event_handler(args.watch)
        event_handler.on_created = self.on_created
        go_recursively = False
        observer = Observer()
        observer.schedule(event_handler, args.watch, recursive=go_recursively)

        return observer

    def get_templates():
        # Not implemented, just for tests
        endpoint = "https://custom-ocr.klippa.com/api/v1/templates"
        request_headers = {"X-Auth-Key": klippa_key, "Content-Type": "application/json"}
        result = requests.get(endpoint, headers=request_headers)
        pretty_json = json.dumps(json.loads(result.text), indent=4)
        with open(f"output/templates3.json", "w") as output_file:
            output_file.write(pretty_json)

    async def encode_to_base64(self, filepath):
        if os.path.isfile(filepath):
            with open(f"{filepath}", "rb") as file:
                byte_content = file.read()
            base64_bytes = b64encode(byte_content)
            base64_string = base64_bytes.decode("UTF-8")

            return base64_string

    async def async_post(self, session, url, args, file):

        request_headers = {
            "X-Auth-Key": args.key, 
            "Content-Type": "application/json"
        }

        base64_string = await self.encode_to_base64(file)

        payload = {"document" : base64_string}
        if args.template:
            payload["template"] = args.template
        if args.text:
            payload["pdf_text_extraction"] = args.text

        async with session.post(
            url, json=payload, headers=request_headers) as response:
            return await response.text()

    async def valid_from_dir(self, session, url, args):
        files = set()
        if os.path.isdir(args.dir):
            for file in os.listdir(args.dir):
                if file.split(".")[1] in self.VALID_TYPES:
                    files.add(args.dir + file)
            tasks = [self.async_post(session, url, args, f) for f in files]
            return await asyncio.gather(*tasks), files
        else:
            print("The filepath of the directory seems to be invalid")
            sys.exit(0)

    async def save_json(self, session, url, args):
        if args.dir:
            req_results, fname = await self.valid_from_dir(session, url, args)
            if not req_results:
                return None
            else:
                for res in req_results:
                    print(json.dumps(json.loads(res), indent=4))
                if args.save:
                    if not os.path.exists('output'):
                        os.makedirs('output')
                    pretty_json = [json.dumps(json.loads(r), indent=4) for r in req_results]
                    right_names = [(Path(f).name).split(".")[0] for f in fname]
                    for res, file in zip(pretty_json, right_names):
                        async with aiofiles.open(f"output/{file}.json", "w") as f:
                            await f.write(res)
                            print(f"Saved to: output/{file}.json")
        else:
            if not os.path.exists(args.file):
                print("The filepath seems to be invalid.")
                sys.exit(0)

            req_results = await self.async_post(session, url, args, args.file)
            if not req_results:
                return None
            else:
                print(json.dumps(json.loads(req_results), indent=4))
                if args.save:
                    if not os.path.exists('output'):
                        os.makedirs('output')
                    pretty_json = json.dumps(
                        json.loads(req_results), indent=4)
                    right_name = (Path(args.file).name).split(".")[0]
                    async with aiofiles.open(f"output/{right_name}.json", "w") as f:
                        await f.write(pretty_json)
                        print(f"Saved to: output/{right_name}.json")

    async def async_handler(self, args):

        # Entry point of async requests loop
        async with aiohttp.ClientSession() as session:
            jobs = []
            jobs.append(self.save_json(session, self.API_URL, args))
            await asyncio.gather(*jobs)

    def on_created(self, event):
        print(f"File {event.src_path} has been added")
        self.ARGS.file = event.src_path
        loop.run_until_complete(app.async_handler(self.ARGS))

if __name__ == "__main__":

    app = Main()
    config = ConfigClient()
    args, extra_args = config.get_args()
    app.ARGS = args
    loop = asyncio.get_event_loop()

    if extra_args == "test":
        # Test new functionality here
        pass
    if extra_args == "watch":
        print("Watching directory:", args.watch)
        print("Press Ctrl+C to stop the script")
        observer = app.create_observer(args)
        observer.start()
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    if extra_args == "file":
        asyncio.run(app.async_handler(args))