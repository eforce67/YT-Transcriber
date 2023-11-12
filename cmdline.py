#!/usr/bin/env python3
import click

from transcribe import Menu  # Import the Menu class from your main script


@click.group()
def cli():
    pass

# Create an instance of the Menu class from your main script
menu = Menu()

@cli.command()
@click.option('--model', prompt='Select the model', help='Select the language model')
def select_model(model):
    """
    Set Model: Select the language model
    """
    menu.select_model()
    menu.save_configuration(menu.configuration)
    print(f'Selected model: {model}')

@cli.command()
@click.option('--attempts', prompt='Enter max download attempts', type=int, help='Set max download attempts')
def set_download_attempts(attempts):
    """
    Set Max Download Attempts: Set the maximum number of download attempts
    """
    menu.configuration['download_attempts'] = attempts
    menu.save_configuration(menu.configuration)
    print(f'Max download attempts set to: {attempts}')

@cli.command()
@click.option('--file', prompt='Enter YouTube links file path', help='Set the path to the YouTube links file')
def set_youtube_links_file(file):
    """
    Set YouTube Links File: Set the path to the YouTube URL text file
    """
    menu.configuration['youtube_links_file'] = file
    menu.save_configuration(menu.configuration)
    print(f'YouTube links file set to: {file}')

@cli.command()
def automate():
    """
    Automate: Load and transcribe links
    """
    menu.load_and_transcribe_links()

@cli.command()
@click.option('--audio', help='The full path to the audio file name.')
def transcribe(audio):
    """
    Transcribe: Transcribe audio from a file
    """
    menu.transcribe_audio(video_file=audio)

@cli.command()
@click.option('--url', help='The youtube video link to download from.')
def download(url):
    """
    Download: Download YouTube audio
    """
    menu.download_youtube_audio(url=url)

@cli.command()
def settings():
    """
    Settings: Configure script settings
    """
    menu.configure_settings()

if __name__ == "__main__":
    cli()
