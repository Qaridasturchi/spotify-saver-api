import io

import os

import uuid

import aiohttp

import datetime

import logging

from fastapi import FastAPI, File, UploadFile, status

from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, RedirectResponse

from shazamio import Shazam

from fastapi.encoders import jsonable_encoder

from spotify_search import SearchFromSpotify

from funcs import DownloadMusic
from fastapi import Query


import requests



import random



from bs4 import BeautifulSoup as BS









def random_ip():



    ips = ['46.227.123.', '37.110.212.', '46.255.69.', '62.209.128.', '37.110.214.', '31.135.209.', '37.110.213.']



    prefix = random.choice(ips)

    return prefix + str(random.randint(1, 255))







shazam = Shazam()



app = FastAPI(

    title="Shazam API",

    description="Shazam API",

    version="1.0.0",

)





# Shazam API

@app.get("/", status_code=status.HTTP_200_OK, description="Welocome to API", response_class=HTMLResponse,

         include_in_schema=False)

async def index():

    # redirect to docs page html code

    html = """<h>HI</h>"""

    return html





@app.post("/shazam/recognize/", status_code=status.HTTP_200_OK, description="Recognize song from audio file",

          tags=['shazam'])

async def recognize(upload_file: UploadFile = File()):

    logging.info("Recognizing song from audio file.")

    _ = ['mp3', 'wav', 'ogg', 'm4a', 'mp4']

    if not upload_file:

        return {"status": False, "message": "No file uploaded"}



    if upload_file.filename.split('.')[-1] not in _:

        print(upload_file.filename.split('.')[-1])

        return {"status": False, "message": "Invalid file format"}

    bytes_file = await upload_file.read()

    if len(bytes_file) > 20971520:

        return {"status": False, "message": "File size is too large"}

    else:

        try:

            searching = await shazam.recognize_song(bytes_file)

            return {"status": True, "result": searching}

        except Exception as e:

            logging.error(f"{datetime.datetime.now()} - {e}")

            return {"status": False, "message": "Something went wrong"}





@app.get("/shazam/recognize/", status_code=status.HTTP_200_OK, description="Recognize song from audio url",

         tags=['shazam'])

async def recognize_url(url: str):

    if not url:

        logging.error(f"{datetime.datetime.now()} - No url provided")

        return {"status": False, "message": "No url provided"}

    else:

        try:

            async with aiohttp.ClientSession() as session:

                async with session.get(url) as resp:

                    if resp.status != 200:

                        logging.error(f"{datetime.datetime.now()} - {resp.status}")

                        result = {"status": False, "message": "Invalid URL"}

                    else:

                        logging.info("Recognizing song from audio url.")

                        bytes_file = await resp.read()

                        if len(bytes_file) > 20971520:

                            result = {"status": False, "message": "File size is too large"}

                        else:

                            result = await shazam.recognize_song(bytes_file)

                        await session.close()

                    return result

        except Exception as e:

            logging.error(f"{datetime.datetime.now()} - {e}")

            return {"status": False, "message": "Something went wrong"}





@app.get("/shazam/search_artist/", status_code=status.HTTP_200_OK, description="Search artist", tags=['shazam'])

async def search_artist(query: str, limit: int = 10):

    if not query:

        logging.error(f"{datetime.datetime.now()} - No query provided")

        return {"status": False, "message": "No query provided"}

    else:

        try:

            logging.info("Searching artist.")

            searching = await shazam.search_artist(query, limit)

            return {"status": True, "result": searching}

        except Exception as e:

            logging.error(f"{datetime.datetime.now()} - {e}")

            return {"status": False, "message": "Something went wrong"}





@app.get("/shazam/search_track/", status_code=status.HTTP_200_OK, description="Search track", tags=['shazam'])

async def search_track(query: str, limit: int = 10):

    if not query:

        logging.error(f"{datetime.datetime.now()} - No query provided")

        return {"status": False, "message": "No query provided"}

    else:

        try:

            logging.info("Searching track.")

            searching = await shazam.search_track(query, limit)

            return {"status": True, "result": searching}

        except Exception as e:

            logging.error(f"{datetime.datetime.now()} - {e}")

            return {"status": False, "message": "Something went wrong"}







@app.get("/download-music/")

async def download_music(track_name: str = Query(..., title="Track Name", description="Name of the track to search"),

                         limit: int = Query(..., title="Limit", description="Limit the number of search results")):

    try:

        track_urls = SearchFromSpotify(track_name, limit)

        audio_urls = DownloadMusic(track_urls)







        return {"downloaded_audio_urls": audio_urls}

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@app.post("/pinterest/")



async def get_pinterest_info(link: str):

    try:

        url = 'https://ssspinterest.com/'

        header = {

            'Origin': 'https://ssspinterest.com',

            'Referer': 'https://ssspinterest.com/',

            'Sec-Ch-Ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',

            'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit'/537.36 (KHTML, like Gecko) Chrome'/112.0.0.0 Mobile Safari'/537.36"

        }

        d = {

            'url': link

        }



        r = requests.post(url, headers=header, data=d)

        r.raise_for_status()  # Raise exception for HTTP errors

        soup = BS(r.text, 'html.parser')

        b = soup.select_one("#quality_1 > option:nth-child(2)")

        a = soup.find("div", class_="download-items")

        if a is not None:

            test = a.text

            i = a.a.get("href")

        else:

            raise HTTPException(status_code=404, detail="Data not found on the page")



        if b is not None:

            result = b["value"]

        else:

            result = i



        return {"result": result}

    except requests.exceptions.RequestException as e:

        raise HTTPException(status_code=500, detail="Error in the external request")

    except Exception as e:

        raise HTTPException(status_code=500, detail="Internal server error")





async def get_mp3_url_yt(youtube_url):

    api_url = 'https://yt5s.io/api/ajaxSearch'

    data = {

        'q': youtube_url,

        'vt': 'mp3'

    }



    async with aiohttp.ClientSession() as session:

        async with session.post(api_url, data=data, headers={'X-Requested-With': 'XMLHttpRequest'}) as response:

            if response.status == 200:

                result = await response.json()

                return result

            else:

                print(f"Xatolik yuz berdi: {response.status}")





async def get_all_mp3_urls(data):

    base_url = 'https://ve44.aadika.xyz/download/'

    video_id = data['vid']

    time_expires = data['timeExpires']

    token = data['token']

    mp3_info_dict = {}



    for index, (quality, info) in enumerate(data['links']['mp3'].items(), start=1):

        if info['f'] == 'mp3':

            mp3_info = {

                'title': data['title'],

                'format': info['k'],

                'q': info['q'],

                'size': info['size'],

                'key': info['key'],

                'url': f"{base_url}{video_id}/mp3/{info['k']}/{time_expires}/{token}/{index}?f=yt5s.io"

            }

            mp3_info_dict[index] = mp3_info



    return mp3_info_dict





@app.get("/youtube/download/audio/", status_code=status.HTTP_200_OK, description="Download audio from Youtube",

         tags=['youtube'])

async def youtube_audio_url(url: str):

    if not url:

        logging.error(f"{datetime.datetime.now()} - No url provided")

        return {"status": False, "message": "No url provided"}

    else:

        try:

            result = await get_mp3_url_yt(url)

            if result['mess'] == "":

                res = await get_all_mp3_urls(result)

                return {"status": True, "result": res}

            else:

                return {"status": False, "message": "Something went wrong"}



        except Exception as e:

            logging.error(f"{datetime.datetime.now()} - {e}")

            return {"status": False, "message": "Something went wrong"}

            

            

            

            

            
