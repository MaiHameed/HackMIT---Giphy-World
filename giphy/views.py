# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from .forms import QueryForm
from unidecode import unidecode
from urllib2 import urlopen, URLError, HTTPError
import os
import giphy_client
import json
import imageio
import requests
import matplotlib
matplotlib.use('TkAgg')
imageio.plugins.ffmpeg.download()

def gif_to_img(name):
    reader = imageio.get_reader(name)
    for i, im in enumerate(reader):
        imageio.imwrite(name + '.jpg', im)

def get_gifs(q):
    q = unidecode(q)
    giphy_api_instance = giphy_client.DefaultApi()
    giphy_api_key = 'dc6zaTOxFJmzC'
    limit = 5
    offset = 0
    rating = 'r'
    lang = 'en'
    fmt = 'json'
    api_response = giphy_api_instance.gifs_search_get(giphy_api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
    names = []
    for i in range(5):
	video = 'tempt' + str(i)
        video_name = video + ".mp4"
	gif_name = video + ".gif"
	try:
            url = api_response.data[i].images.fixed_height.mp4
            f = urlopen(url)
            with open(os.path.basename(video_name), "wb") as local_file:
                local_file.write(f.read())
        except HTTPError, e:
            print "HTTP Error:", e.code, url
        except URLError, e:
            print "URL Error:", e.reason, url
	names.append(tuple((os.path.basename(video_name), api_response.data[i].images.fixed_height.url)))
    return names 

def azure_assess(name):
    subscription_key = "d483db15e84e4f5983055f85036a8612"
    assert subscription_key
    vision_base_url = "https://eastus.api.cognitive.microsoft.com/vision/v1.0/"
    analyze_url = vision_base_url + "analyze"
    image_path = name
    image_data = open(os.path.basename(image_path), "rb").read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
                  'Content-Type': 'application/octet-stream'}
    params     = {'visualFeatures': 'Adult'}
    response = requests.post(
        analyze_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()
    analysis = response.json()
    return(analysis['adult']['isAdultContent'] or analysis['adult']['isRacyContent'])


def index(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            textarea = form.cleaned_data['textarea']
            names = get_gifs(textarea)
            approved = []
            for name in names:
                gif_to_img(name[0])
		if not (azure_assess(name[0] + '.jpg')):
			approved.append(name[1])
            return render(request, 'giphy/giffy.html', {'gifs':approved})
    else:
        form = QueryForm()
    return render(request, 'giphy/index.html', {'form':form})
