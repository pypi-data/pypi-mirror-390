

from typing import Union, Literal
from pathlib import Path
import pkg_resources

alarm_done_path = pkg_resources.resource_filename(__name__, 'assets/Sound Effect positive-logo-opener.wav')
alarm_error_path = pkg_resources.resource_filename(__name__, 'assets/Sound Effect Error.wav')

def play_audio_file(audio_path:Union[Path,str],
               engine:Literal["auto","simpleaudio","pydub","playsound"] = "auto") -> None:
    """
    
    provided user with multiple option of packages for playing audio

    Parameters
    ----------
    audio_path : Union[Path,str]
        DESCRIPTION.
    engine : Literal["auto","simpleaudio","pydub","playsound"], optional
        DESCRIPTION. The default is "auto".

    Returns
    -------
    None.

    """
    # fix bug in case users don't install simpleaudio
    
    try:
        from pydub import AudioSegment
        from pydub.playback import play
        audio = AudioSegment.from_mp3(str(audio_path))
    except:
        pass

    try:
        import simpleaudio as sa
        # simpleaudio requires Microsoft Visual C++ 14.0.
        #  Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
        wave_obj = sa.WaveObject.from_wave_file(str(audio_path))
    except:
        pass
    
    
    if engine in ["auto"]:
        try:
            from playsound import playsound
            # playsound
            playsound(str(audio_path))
        except:
            try:
                # simpleaudio
                play_obj = wave_obj.play()
            except:
                # pydub
                play(audio)
                
    elif engine in ["simpleaudio"]:
        import simpleaudio as sa
        play_obj = wave_obj.play()
    elif engine in ["pydub"]:
        play(audio)
    elif engine in ["playsound"]:
        from playsound import playsound
        playsound(str(audio_path))

def play_alarm_done():
    play_audio_file(alarm_done_path)

def play_alarm_error():
    play_audio_file(alarm_error_path)