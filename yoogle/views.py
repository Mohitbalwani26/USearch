from django.shortcuts import render, redirect
from django.http import HttpResponse
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Create your views here.


def _get_video_id(video_url):
    regex_pattern = r"^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*"
    valid_matches = re.findall(regex_pattern, video_url)
    if valid_matches and len(valid_matches[0][1]) == 11:
        return valid_matches[0][1]
    return -1


def _get_occurence(transcript, keyword):

    arr = []
    for slot in transcript:
        if keyword.lower() in slot["text"].lower():
            arr.append(round(slot['start']))

    return arr


def index(request):
    context = {}
    error = ''
    if request.method == 'POST':
        video_url = request.POST.get('url')
        keyword = request.POST.get('keyword')
        context['keyword'] = keyword
        context['video_url'] = video_url
        video_id = _get_video_id(video_url)
        all_occurences = []
        if video_id == -1:
            error = "Enter valid URL"
        else:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                all_occurences = _get_occurence(transcript, keyword)

            except:
                error = "Couldn't find transcript file for the given video"

            if all_occurences:
                video_embedded = "https://www.youtube.com/embed/{id}?start={first}".format(
                    id=video_id, first=all_occurences[0])
            else:
                video_embedded = "https://www.youtube.com/embed/{id}?start={first}".format(
                    id=video_id, first=0)
            urls = {}
            for timestamp in all_occurences:
                h, m, s = timestamp//3600, timestamp//60, timestamp % 60
                if h > 0:
                    key = '{h}:{m}:{s}'.format(
                        h=str(h).zfill(2), m=str(m).zfill(2), s=str(s).zfill(2))
                else:
                    key = '{m}:{s}'.format(
                        m=str(m).zfill(2), s=str(s).zfill(2))
                urls[key] = "https://www.youtube.com/embed/{id}?start={first}".format(
                    id=video_id, first=timestamp)

            context['video_embedded'] = video_embedded
            context["error"] = error
            context['all_occurences'] = all_occurences
            context['urls_array'] = urls

    return render(request, 'yoogle/index.html', context)
