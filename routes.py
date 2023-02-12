import os
import re
import urllib.request
from pytube import YouTube
from pydub import AudioSegment
from flask import Flask, render_template, request
import sys
from flask import Flask,render_template, request,redirect,url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('mashup'))

    # return render_template("index.html")





@app.route("/mashup", methods=["GET", "POST"])
def mashup():
    if request.method == "POST":
        search_query = request.form.get("search_query").strip().replace(" ", "") + "songs"
        num_videos = int(request.form.get("num_videos"))
        audio_length = int(request.form.get("audio_length"))
        output_filename = request.form.get("output_filename")
        email_recipient = request.form.get("email_recipient")
        print(search_query,num_videos,audio_length,output_filename,email_recipient)
        if num_videos < 1 or audio_length < 2:
            return "Number of videos and audio length must be greater than 10 and 20 respectively", 400

        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_query}")
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        audio_files = []
        for i in range(num_videos):
            video = YouTube(f"https://www.youtube.com/watch?v={video_ids[i]}")
            audio_file = video.streams.filter(only_audio=True).first().download(filename=f"tempaudio-{i}.mp3")
            audio_files.append(audio_file)

        final_audio = AudioSegment.from_file(audio_files[0])[:audio_length * 1000]
        for audio_file in audio_files[1:]:
            final_audio = final_audio.append(AudioSegment.from_file(audio_file)[:audio_length * 1000], crossfade=1000)

        final_audio.export(output_filename, format="mp3")

        for audio_file in audio_files:
            os.remove(audio_file)
        
        # send email with the mashup file as an attachment
        email = MIMEMultipart()
        email['from'] = "tarandeep293@gmail.com"
        email['to'] = email_recipient
        email['subject'] = "Mashup file"
        email.attach(MIMEText("Please find the attached mashup file."))
        with open(output_filename, 'rb') as f:
            file = MIMEApplication(f.read(),_subtype="mp3")
            file.add_header('content-disposition', 'attachment', filename=output_filename)
            email.attach(file)
        

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login("tarandeep293@gmail.com", "fvzskjmqpregnbhl")
        server.sendmail("tarandeep293@gmail.com", email_recipient, email.as_string())
        server.quit()

        return "Mashup created and sent to email successfully!", 200

    # return """
    #     <form action='/mashup' method='post'>
    #         Search query: <input type='text' name='search_query'>
    #         Number of videos: <input type='number' name='num_videos'>
    #         Audio length: <input type='number' name='audio_length'>
    #         Output filename: <input type='text' name='output_filename'>
    #         <input type='submit' value='Create Mashup'>
    #     </form>
    # """

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug="TRUE")
