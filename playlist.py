# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START sheets_quickstart]
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp
import re
import sys

# python3 playlist.py  "PLqdswNfykL2yQMZ2U5bOmCl9bLNfvh6mK"

def main(playlistId):
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """

  # If modifying these scopes, delete the file token.json.
  SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=59865)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("youtube", "v3", credentials=creds)

    # Get the youtube items.
    playlistItems = service.playlistItems()
    request = playlistItems.list(
        part="snippet",
        maxResults=25,
        playlistId = playlistId
    )
    response = request.execute()

    # Create playlist directory.
    path = 'downloads/' + playlistId
    isExist = os.path.exists(path)
    if not isExist:

      # Create a new directory because it does not exist
      os.makedirs(path)
      print("The new directory " + path + " is created!")

    # Get all files from youtube downloads dir.
    files = {}
    for f in os.listdir(path):
      if os.path.isfile(path + '/' + f) & f.endswith('.mp4'):
       match = re.search(r'\[([\w\-_]*)\]', f)
       videoId = match.group(1)
       files[videoId] = f

    # Download the youtube video.
    removeFiles = files
    for i in response["items"]:
        videoId = i["snippet"]["resourceId"]["videoId"]
        if videoId in files:
          print("Video alredy exists: " + videoId)
          # Delete from the remove list if the video exists in the list.
          del removeFiles[videoId]
          continue

        print("Downloading " + videoId)
        URL = 'https://www.youtube.com/watch?v=' + videoId

        # Download the youtbe video.
        with yt_dlp.YoutubeDL({'format':'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': path + '/' + '/[%(id)s] - %(title)s.%(ext)s'}) as ydl:
            ydl.download([URL])

    # Delete videos that does not exists on the youtube playlist.
    if len(removeFiles) > 0:
      for f in removeFiles:
        print("Removing deprecated video: " + removeFiles[f])
        os.remove(path + '/' + removeFiles[f])

  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main(sys.argv[1])
# [END sheets_quickstart]
