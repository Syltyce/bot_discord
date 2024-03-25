from pytube import YouTube
from moviepy.editor import VideoFileClip

# Fonction qui permet de télécharger une vidéo YouTube (entièrement)
async def download_video(video_url, output_path):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path)
        return True, f"La vidéo a été téléchargée avec succès sous {output_path}"
    except Exception as e:
        return False, f"Une erreur s'est produite lors du téléchargement de la vidéo : {str(e)}"
    
# Fonction qui permet de télécharger et spliter une vidéo YouTube en plusieurs extraits de 1 minute
async def download_and_split_video(video_url, output_folder):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        video_path = stream.download(output_folder)

        # Charger la vidéo avec MoviePy
        video_clip = VideoFileClip(video_path)

        # Durée totale de la vidéo
        total_duration = video_clip.duration

        # Durée des extraits (1 minute)
        clip_duration = 60

        # Découper la vidéo en extraits de 1 minute
        start_time = 0
        while start_time < total_duration:
            end_time = min(start_time + clip_duration, total_duration)
            clip = video_clip.subclip(start_time, end_time)
            clip_output_path = f"{output_folder}/extract_{start_time}-{end_time}.mp4"
            clip.write_videofile(clip_output_path)
            start_time += clip_duration

        # Supprimer le fichier vidéo original
        video_clip.close()
        return True, "La vidéo a été téléchargée et découpée avec succès."
    except Exception as e:
        return False, f"Une erreur s'est produite lors du téléchargement et de la découpe de la vidéo : {str(e)}"

