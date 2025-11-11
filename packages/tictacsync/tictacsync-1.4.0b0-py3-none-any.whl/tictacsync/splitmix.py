import argparse, sys, sox
from loguru import logger
from scipy.io.wavfile import write as wrt_wav

try:
    from . import load_fieldr_reaper
    from . import yaltc
except:
    import load_fieldr_reaper
    import yaltc




logger.level("DEBUG", color="<yellow>")
logger.add(sys.stdout, level="DEBUG")
# logger.remove()

def conf_and_parse_arguments():
    # parses directories from command arguments
    # check for consistencies and warn user and exits,
    # returns parser.parse_args()
    descr = "Parse the submitted OTIO timeline and split the specified mix wav file according to OTIO clips"
    parser = argparse.ArgumentParser(description=descr) 
    parser.add_argument(
                "otio_file",
                type=str,
                nargs=1,
                help="path of timeline saved under OTIO format"
                )
    parser.add_argument('mix',
                    type=str,
                    nargs=1,
                    help="mix wav file to be splitted")
    args = parser.parse_args()
    logger.debug('args %s'%args)
    return args

# def write_wav(file, audio, samplerate):
#     # Put the channels together with shape (2, 44100).
#     # audio = np.array([left_channel, right_channel]).T

#     audio = (audio * (2 ** 15 - 1)).astype("<h")

#     with wave.open(file, "w") as f:
#         # 2 Channels.
#         f.setnchannels(2)
#         # 2 bytes per sample.
#         f.setsampwidth(2)
#         f.setframerate(samplerate)
#         f.writeframes(audio.tobytes())


def main():
    # [TODO] split but duplicate audio to fill in the trimed parts of each clip
    # so use whole clip duration rather than cut_duration for audio length
    args = conf_and_parse_arguments()
    fps, clips =load_fieldr_reaper.read_OTIO_file(args.otio_file[0])
    logger.debug(f'otio has {fps} fps')
    wav_file = args.mix[0]
    N_channels = sox.file_info.channels(wav_file)
    logger.debug(f'{wav_file} has {N_channels} channels')
    tracks = yaltc.read_audio_data_from_file(wav_file, N_channels)
    audio_data = tracks.T # interleave channels for cutting later
    logger.debug(f'audio data shape {audio_data.shape}')
    logger.debug(f'data: {tracks}')
    logger.debug(f'tracks shape {tracks.shape}')
    # start_frames, the "in" frame number (absolute, ie first "in" is 0)
    start_frames = [int(round(cl.timeline_pos*fps)) - 3600*fps for cl in clips]
    logger.debug(f'start_frames {start_frames}')
    durations = [int(round(cl.cut_duration*fps)) for cl in clips]
    logger.debug(f'durations {durations}')
    # sampling frequency, samples per second
    sps = sox.file_info.sample_rate(wav_file)
    # number of audio samples per frames, 
    spf = sps/fps
    logger.debug(f'there are {spf} audio samples for each frame')
    audio_slices = [audio_data[int(spf*s):int(spf*(s+d))] for s,d in zip(start_frames, durations)]
    logger.debug(f'audio_slices lengths {[len(s) for s in audio_slices]}')
    for a in audio_slices:
        logger.debug(f'audio_slices {a}')

    [wrt_wav(f'{clips[i].name.split(".")[0]}.wav', int(sps), a) for i, a in enumerate(audio_slices)]


if __name__ == '__main__':
    main()
