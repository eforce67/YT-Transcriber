#!/usr/bin/env python3
import http
import os

import inquirer
import pandas as pd
import yaml
from faster_whisper import WhisperModel
from pytube import YouTube


class Menu:
    def __init__(self):
        self.CONFIG_PATH = './config.yaml'
        with open(self.CONFIG_PATH, 'r') as config_file:
            config = yaml.safe_load(config_file)
            
        self.configuration = config
        
    def save_configuration(self, config):
        with open(self.CONFIG_PATH, 'w') as config_file:
            yaml.dump(config, config_file, default_flow_style=False)
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def select_model(self):
        options = [
            inquirer.List('model',
                          message="Select the model:",
                          choices=['tiny.en', 'tiny', 'base.en', 'base','small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2',],
            )
        ]
        choice = inquirer.prompt(options)['model']
        self.configuration['selected_model'] = choice
        print(f'[+] {choice} selected')

    def set_download_attempts(self):
        options = [
            inquirer.Text('download_attempts',
                          message="Enter the max number of download attempts:",
                          validate=lambda _, x: x.isdigit(),
            )
        ]
        max_attempts = inquirer.prompt(options)['download_attempts']
        self.configuration['download_attempts'] = int(max_attempts)

    def set_youtube_links_file(self):
        options = [
            inquirer.Text('youtube_links_file',
                          message="Enter the path to the YouTube URL text file:",
            )
        ]
        path = inquirer.prompt(options)['youtube_links_file']
        self.configuration['youtube_links_file'] = path

    def set_configuration_option(self, option):
        menu_options = {
            '1': self.select_model,
            '2': self.set_download_attempts,
            '3': self.set_youtube_links_file,
            'x': self.show_menu,
            'c': self.clear_screen
        }

        if option in menu_options:
            menu_options[option]()
        self.save_configuration(self.configuration)
    
    def load_and_transcribe_links(self):
        links_file = self.configuration['youtube_links_file']
        print('State: Attempting to load Youtube links file...')
        if not os.path.isfile(links_file):
            print(f'Error: YouTube links file "{links_file}" not found.')
            return
        try:
            links_df = pd.read_csv(links_file, header=None)
            for _, row in links_df.iterrows():
                url = row[0]
                output = self.download_youtube_audio(url)
                self.transcribe_audio(video_file=output)
        except pd.errors.EmptyDataError:
            print('Could not read "empty" data from youtube link file...')

    def download_youtube_audio(self, url):
        max_attempts = int(self.configuration['download_attempts'])

        for _ in range(max_attempts):
            try:
                youtube = YouTube(url)
                
                audio_stream = youtube.streams.filter(only_audio=True, file_extension='mp4').first()
                print('State: Searching Youtube...')
                if audio_stream:
                    video_title = ''.join(['_' if not letter.isalnum() else letter for letter in youtube.title]) + '.mp3'
                    audio_stream.download(output_path='./', filename=video_title)
                    print(f'Downloaded: {video_title}')
                    return video_title
                else:
                    print(f'No audio stream found for {youtube.title}.')
            except Exception as e:
                if isinstance(e, http.client.IncompleteRead):
                    print('IncompleteRead Error: Data reception interrupted. Check data source, network stability, and error handling.')
                print(f'Error: {e}')
        else:
            print(f'Max download attempts reached for {url}.')
        
    def transcribe_audio(self, video_file):
        if not video_file.endswith(".mp3"):
            print(f'Error: File "{video_file}" is not in mp3 format.')
            return

        output_file_name = video_file.replace('.mp3', '.csv')  # Change the output format to CSV

        try:
            print('State: Loading Whisper model')
            model = WhisperModel(self.configuration.get('selected_model'), device=self.configuration.get('device'), compute_type=self.configuration.get('compute'))
            print('State: Transcribing audio')
            segments, info  = model.transcribe(video_file, beam_size=5, vad_filter=True)
            
            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            print('State: Writing audio to CSV')  # Changed from text to CSV
            
            data = []
            chunksize = 600  # Adjust the chunk size as needed

            for idx, segment in enumerate(segments):
                data.append([idx + 1, f'{segment.start:.2f}', f'{segment.end:.2f}', segment.text.strip()])

                # Check if it's time to write a chunk to the CSV
                if (idx + 1) % chunksize == 0:
                    self.write_data_to_csv(output_file_name, data, idx)
                    data = []

            # Write any remaining data to the CSV
            if data:
                self.write_data_to_csv(output_file_name, data, idx, append=True)
                os.remove(video_file)
                print(f'State: Finished, transcription saved to: {output_file_name}')
        except Exception as e:
            print(f'Error: {e}')

    def write_data_to_csv(self, output_file_name, data, idx, append=False):
        df = pd.DataFrame(data, columns=['Index', 'From', 'To', 'Text'])
        mode = 'a' if append else 'w' if idx == 0 else 'a'
        header = not append and idx == 0
        df.to_csv(f'./transcriptions/{output_file_name}', mode=mode, index=False, header=header)
    
    def configure_settings(self):
        settings_options = [
            inquirer.List('setting',
                          message="Settings Menu:",
                          choices=[
                              ('Set Model', '1'),
                              ('Set Max Download Attempts', '2'),
                              ('Set YouTube Links File', '3'),
                              ('Cancel', 'x'),
                              ('Clear Screen', 'c')
                              ]
                          )
            ]
        option = inquirer.prompt(settings_options)['setting']
        self.set_configuration_option(option)
        print('successfully saved configuration')
        self.configure_settings() # reload the screen

    def show_menu(self):
        menu_options = {
            '1': self.load_and_transcribe_links,
            '2': lambda: self.download_youtube_audio(url=input("Enter the YouTube URL Link: ")),
            '3': lambda: self.transcribe_audio(video_file=input('Enter the file to transcribe (must be in the same directory): ')),
            '4': self.configure_settings,
            'x': exit,
            'c': self.clear_screen
        }
        choice = self.display_menu_select()

        if choice in menu_options:
            menu_options[choice]()
        self.show_menu()

    def display_menu_select(self):
        options = [
            inquirer.List('menu',
                          message="Select the action for the script to perform!",
                          choices=['Automate', 'Download Videos', 'Transcribe', 'Settings', 'Exit', 'Clear Screen'],
            )
        ]
        choice = inquirer.prompt(options)['menu']
        return {
            'Automate': '1',
            'Download Videos': '2',
            'Transcribe': '3',
            'Settings': '4',
            'Exit': 'x',
            'Clear Screen': 'c'
        }.get(choice, '')

if __name__ == '__main__':
    menu = Menu()
    menu.show_menu()
