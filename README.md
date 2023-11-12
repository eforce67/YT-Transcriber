# YT-Transcriber 
This project aims to download YouTube videos and transcribe them using Open-AI Whisper's models!

# Benefits of what the script can do:
- Uses __faster-whisper__ for improvement in performance.
- When chunk size is reached (which is 600), the script writes the data into the CSV file.
- User-friendly interface using Inquirer, including an interactive setting for configuration.
- Configuration Handling inside config.yml and a CSV Output for Transcriptions.
- Fully automated transcription process.

# What the script cannot do:
- Only transcribes **mp3** audio files, but you can easily modify the code to add support for your use cases.
- Limited Error handling, although you could create an issue and ask for help!
- Can only download videos from YouTube

> [!NOTE]
> If you're attempting to use Openai whisper-large-v3, It might work if you could get it to work with faster-whisper first.

## This project wouldn't be possible but thanks to these guys it is, so check them out!
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [pytube](https://github.com/pytube/pytube)
