import os, itertools, argparse, ffmpeg, tempfile, platformdirs, pathlib
from enum import Enum
from pathlib import Path
import shutil, sys, re, sox, configparser
from pprint import pformat
from rich import print
import numpy as np
from scipy.io.wavfile import write as wrt_wav
import rich.progress, uuid

try:
    from . import mamconf
    from . import yaltc
    from . import mamreap
except:
    import mamconf
    import yaltc
    import mamreap

from loguru import logger

ONE_HR_START = 3600

LUA = True
OUT_DIR_DEFAULT = 'SyncedMedia'
MCCDIR = 'SyncedMulticamClips'
SEC_DELAY_CHANGED_SND = 1 #sec, SND_DIR changed if diff time is bigger [why not zero?]
DEL_TEMP = False
CONF_FILE = 'mamsync.cfg'

logger.remove()
# logger.add(sys.stdout, level="DEBUG")

# logger.level("DEBUG", color="<yellow>")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "find_SND_vids_pairs_in_dual_dir")
# logger.add(sys.stdout, filter=lambda r: r["function"] == "read_OTIO_file")

v_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp""".split()


DAVINCI_RESOLVE_SCRIPT_LOCATION = '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/'

DAVINCI_RESOLVE_SCRIPT_TEMPLATE_LUA = """local function ClipWithPartialPath(partial_path)
    local media_pool = app:GetResolve():GetProjectManager():GetCurrentProject():GetMediaPool()
    local queue = {media_pool:GetRootFolder()}
    while #queue > 0 do
        local current = table.remove(queue, 1)
        local subfolders = current:GetSubFolderList()
        for _, folder in ipairs(subfolders) do
            table.insert(queue, folder)
        end
        local got_it = {}
        local clips = current:GetClipList()
        for _, cl in ipairs(clips) do
            if string.find(cl:GetClipProperty('File Path'), partial_path) then
                table.insert(got_it, cl)
            end
        end
        if #got_it > 0 then
            return got_it[1]
        end
    end
end

local function findAndReplace(trio)
    local old_file = trio[2]
    local new_file = trio[3]
    local name = trio[1]
    local clip_with_old_file = ClipWithPartialPath(old_file)
    if clip_with_old_file == nil then
        print('did not find clip with path ' .. old_file)
    else
        clip_with_old_file:ReplaceClip(new_file)
        local cfp = clip_with_old_file:GetClipProperty('File Path')
        clip_with_old_file:SetClipProperty('Clip Name', name)
        local cn = clip_with_old_file:GetClipProperty('Clip Name')
        if cfp == new_file then
            print('Loaded ' .. cn .. ' with a new sound track')
        else
            print('findAndReplace ' .. old_file .. ' -> ' .. new_file .. ' failed')
        end
    end
end

local changes = {
"""

video_extensions = \
"""webm mkv flv flv vob ogv  ogg drc gif gifv mng avi mov 
qt wmv yuv rm rmvb viv asf  mp4  m4p m4v mpg  mp2  mpeg  mpe 
mpv mpg  mpeg  m2v m4v svi 3gp 3g2 mxf roq nsv""".split() # from wikipedia

def rint(x):
    return int(round(x))

# logger.add(sys.stdout, filter=lambda r: r["function"] == "_vid_stem")
def _vid_stem(video):
    # from a video name (str or pathlib.Path)
    # return the stem without any version letter
    # e.g.: canon24fps01_vagygg8789732hj..32..65765.MOV -> canon24fps01
    if not isinstance(video, pathlib.Path):
        video = pathlib.Path(video)
    if not '_v' in video.name:
        return video.stem
    m = re.match(r'(?P<stem>.+?)_v(\w{32})', video.name)
    logger.debug(f're.match.groups:  {m.groups()}')
    if m == None:
        print(f'Error trying to process name {video} ; Bye.')
        sys.exit(0)
    logger.debug(f'stem: {m.group("stem")} from {video}')
    return m.group('stem')

class Modes(Enum):
    INTRACLIP = 1 # send-to-pict <no args> 
                 # scans SNDROOT and finds new mixes more recent than
                 # their video counterparts and merge them.

    INTERCLIP_SOME = 2 # send-to-pict <otio_stem>
                   # looks into SNDROOT/Sound_Edits and find specified trio
                   # SoundForMyMovie/Sound_Edits/<otio_stem>_mix.wav
                   # SoundForMyMovie/Sound_Edits/<otio_stem>.otio
                   # SoundForMyMovie/Sound_Edits/<otio_stem>.mov <- with TC!

    INTERCLIP_ALL = 3 # send-to-pict <otio_stem>
                  # looks into SNDROOT/Sound_Edits and find specified duo
                  # SoundForMyMovie/Sound_Edits/<otio_stem>_mix.wav
                  # SoundForMyMovie/Sound_Edits/<otio_stem>.otio

# logger.add(sys.stdout, filter=lambda r: r["function"] == "parse_args_for_mode_and_files")
def parse_args_for_mode_and_files():
    """
    Parses command arguments and determines mode and associated files.
    Checks for inconsistencies and warn user and exits.
    
    There are two major modes: intraclip or interclip.
    intraclip: only a clip name is needed, even partial, e.g.: DSC_8064
    interclip: an otio file and a wav mix is needed, opt. a rendered video.

    Will look for three files in the same directory (interclip):
        an otio file
        a wav mix file
        an optional video file
    each file starts with the same prefix and the mix file should fit the
    <pre>_mix.wav pattern, e.g.:
        cut42.otio
        cut42_mix.wav
        cut42.mov

    so one could call: mamdav /foo/edits/cut42*

    Returns tuple of (mode, otio_path, movie_path, wav_path)
    """
    descr = "Create a DaVinci Resolve script to reload videos whose audio track has been modified."
    parser = argparse.ArgumentParser(description=descr) 
    parser.add_argument(
                    nargs='*',
                    dest='otio_mix_files', # mamdav cut27*
                    help='name of the clip, or otio & wav files to be used')
    parser.add_argument('-c',
                    action='store_true',
                    help="clear any version number from Resolve MediaPool and exit.")
    args = parser.parse_args()
    logger.debug('args %s args.otio_mix_files %s'%(args, args.otio_mix_files))
    if args.c:
        pass # [TODO] clear sunced_root or Resolve via otio?
    if args.otio_mix_files == []:
        return Modes.INTRACLIP, None, None, None ###############################
    # in args.otio_mix_files, find which one is otio, which one is wav
    # and maybe which one is a video, doing so, determine the mode
    omfp = [pathlib.Path(f) for f in args.otio_mix_files]
    otio = [p for p in omfp if p.suffix.lower() == '.otio']
    if len(otio) != 1:
        print(f'Error, problem finding otio file in {args.otio_mix_files}, bye.')
        sys.exit(0)
    otio_path = otio[0]
    wav = [p for p in omfp if p.suffix.lower() == '.wav']
    if len(wav) != 1:
        print(f'Error, problem finding wav file in {args.otio_mix_files}, bye.')
        sys.exit(0)
    wav_path = wav[0]
    # check cut42.otio -> cut42_mix.wav
    # first, check _mix.wav?
    if '_' not in str(wav_path.name) or str(wav_path.name).split('_')[1].lower() != 'mix.wav':
        print(f'Error, {wav_path.name} doesnt contain "_mix.wav", bye.')
        sys.exit(0)
    # cut42* for both?
    if otio_path.stem != str(wav_path.name).split('_')[0]:
        print(f'Error, {otio_path} and {wav_path} dont have the same prefix, bye.')
        sys.exit(0)
    if len(omfp) == 2:
        # [TODO] we're done, mode is Modes.INTERCLIP_ALL 
        # Modes.INTERCLIP_SOME will be implemented later...
        mode = Modes.INTERCLIP_ALL
        movie_path = None
        logger.debug(f'mode, otio_path, movie_path, wav_path:')
        logger.debug(f'{mode}, {otio_path}, {movie_path}, {wav_path}.')
        return mode, otio_path, movie_path, wav_path ##########################
    # if len(args.otio_mix_files), check 3rd is video
    def _neither_otio_wav(p):
        suf = p.suffix.lower()
        return suf not in  ['.otio', '.wav'] 
    other = [p for p in omfp if _neither_otio_wav(p)]
    movie_path = other[0]
    if len(other) != 1 or movie_path.suffix[1:] not in v_file_extensions:
        print(f'Error, cant find video file in {other}, bye.')
        sys.exit(0)
    mode = Modes.INTERCLIP_SOME
    logger.debug(f'mode, otio_path, movie_path, wav_path:')
    logger.debug(f'{mode}, {otio_path}, {movie_path}, {wav_path}.')
    print('Sorry, INTERCLIP_SOME not yet implemented, bye')
    sys.exit(0)
    return mode, otio_path, movie_path, wav_path ##############################

def _pathname(tempfile_or_path) -> str:
    # utility for obtaining a str from different filesystem objects
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def is_synced_video(f):
    # True if name as video extension
    # and is under SyncedMedia or SyncedMulticamClips folders
    # f is a Path
    ext = f.suffix[1:] # removing leading '.'
    ok_ext = ext.lower() in video_extensions
    f_parts = f.parts
    ok_folders = OUT_DIR_DEFAULT in f_parts or MCCDIR in f_parts
    # logger.debug('ok_ext: %s ok_folders: %s'%(ok_ext, ok_folders))
    return ok_ext and ok_folders

def _names_match(vidname, SND_name):
    # vidname is a str and has no extension
    # vidname could have v<uuid> suffix as in DSC_8064_v03e3f5d2bc3d11f0a8d038c9864d497d so matches DSC_8064
    if vidname == SND_name: # no suffix presents 
        return True
    # m = re.match(SND_name + r'v(\d+)', vidname)
    m = re.match(SND_name + r'_v(\w{32})', vidname)
    if m != None:
        logger.debug('its a match and letter= %s for %s'%(m.groups()[0], vidname))
    return m != None

def find_SND_vids_pairs_in_dual_dir(synced_root, snd_root):
    # look for matching video stem (without _v*) and SND in the two argument directories
    # eg: IMG04_v13ab..cde.mov and directory IMG04_SND
    # returns dict of (key: vid stem; value: paths tuple), where  vid is str and
    # paths_tuple a tuple of found pathlib.Path (vid path, SND dir)
    # recursively search from 'top' argument
    vids = []
    SNDs = []
    print(f'Will look for new mix in {snd_root} compared to vids in {synced_root}')
    for (root,dirs,files) in os.walk(synced_root):
        for f in files:
            pf = Path(root)/f
            if pf.suffix[1:].lower() in video_extensions:
                if not pf.is_symlink():
                    vids.append(pf)
    for (root,dirs,files) in os.walk(snd_root):
        for d in dirs:
            if d[-4:] == '_SND':
                SNDs.append(Path(root)/d)
    logger.debug('vids %s SNDs %s'%(pformat(vids), pformat(SNDs)))
    # check for name collision in vids
    vid_stems_set = set([_vid_stem(f) for f in vids])
    vid_stems = [_vid_stem(f) for f in vids]
    if len(vid_stems_set) != len(vid_stems):
        print('Error, there are name collision in clip names:')
        vid_stems.sort()
        for vs in vid_stems:
            print(vs)
        print('\nBye.')
        sys.exit(0)
    matches = {}
    for pair in list(itertools.product(SNDs, vids)):
        SND, vid = pair # Paths
        vidname = vid.stem
        if _names_match(vidname, SND.name[:-4]):
            logger.debug('SND %s matches video %s'%(
                Path('').joinpath(*SND.parts[-2:]),
                Path('').joinpath(*vid.parts[-3:])))
            # matches.append(pair) # list of Paths
            matches[_vid_stem(vid)] = (vid, SND) # 
    logger.debug('matches: %s'%pformat(matches))
    return matches

def get_recent_mix(SND_dir, vid):
    # search for a mix file in SND_dir
    # and return the mix pathib.Path if it is more recent than vid.
    # returns empty tuple otherwise
    # arguments SND_dir, vid and returned values are of Path type
    wav_files = list(SND_dir.iterdir())
    logger.debug(f'wav_files {wav_files} in {SND_dir}')
    def is_mix(p):
        re_result = re.match(r'.*mix.*', p.name)
        logger.debug(f'for {p.name} re_result looking for mix {re_result}')
        return re_result is not None
    mix_files = [p for p in wav_files if is_mix(p)]
    if len(mix_files) == 0:
        return ()
    if len(mix_files) != 1:
        print(f'\nError: too many mix files in [bold]{SND_dir}[/bold], bye.')
        [print(f) for f in mix_files]
        sys.exit(0)
    mix = mix_files[0]
    logger.debug(f'mix: {mix}')
    # check dates, if two files, take first
    mix_modification_time = mix.stat().st_mtime
    vid_mod_time = vid.stat().st_mtime
    # difference of modification time in secs
    mix_more_recent_by = mix_modification_time - vid_mod_time
    logger.debug('mix_more_recent_by: %s'%mix_more_recent_by)
    if mix_more_recent_by > SEC_DELAY_CHANGED_SND:
        # if len(mix_files) == 1:
            # two_folders_up = mix_files[0]
            # two_folders_up = Path('').joinpath(*mix_files[0].parts[-3:])
        # print(f'\nFound new mix: [bold]{mix}[/bold]')
        return mix
    else:
        return None

def _keep_VIDEO_only(video_path):
    # return file handle to a temp video file formed from the video_path
    # stripped of its sound
    in1 = ffmpeg.input(_pathname(video_path))
    video_extension = video_path.suffix
    silenced_opts = ["-loglevel", "quiet", "-nostats", "-hide_banner"]
    file_handle = tempfile.NamedTemporaryFile(suffix=video_extension,
        delete=DEL_TEMP)
    out1 = in1.output(file_handle.name, map='0:v', vcodec='copy')
    ffmpeg.run([out1.global_args(*silenced_opts)], overwrite_output=True)
    return file_handle

# logger.add(sys.stdout, filter=lambda r: r["function"] == "_build_new_names")
def _build_new_names(video: Path):
    """
    If name has version letter, upticks it it (DSC_8064vB.MOV -> DSC_8064vC.MOV)
    Returns string tuple of old and new video files.
    Old file is partial (without version and suffix) e.g.: ../DSC_8064 so
    Resolve Lua script can find it in its MediaPool;
    new file is complete.
    Returns str tuple: partial_filename and out_n
    """
    vidname, video_ext = video.name.split('.')
    # check v suffix
    m = re.match(r'(.*?)_v(\w{32})', vidname)
    logger.debug(f' for {vidname}, regex match {m}')
    ID = uuid.uuid1().hex
    if m == None:
        logger.debug('no suffix, add one {ID}')
        out_path = video.parent / f'{vidname}_v{ID}.{video_ext}'
        out_n = _pathname(out_path)
        # for Resolve search
        partial_filename = str(video.parent / vidname) # vidname has no 'v' here
    else:
        base, old_uuid = m.groups()
        logger.debug(f'base {base}, old_uuid {old_uuid}')
        # new_letter = chr((ord(letter)+1 - 65) % 26 + 65) # next one
        # logger.debug(f'new_letter {new_letter}')
        out_path = video.parent / f'{base}_v{ID}.{video_ext}'
        out_n = _pathname(out_path)
        # for Resolve search
        partial_filename = str(video.parent / base)
    logger.debug(f'new version {out_n}')
    return partial_filename, out_n

# logger.add(sys.stdout, filter=lambda r: r["function"] == "_change_audio4video")
def _change_audio4video(audio_path: Path, video: Path):
    """
    Replaces audio in video (argument)  by the audio contained in
    audio_path (argument)
    Returns str tuple (partial_filename, new_file) see _build_new_names
    """
    partial_filename, new_file = _build_new_names(video)
    # print(f'Video [bold]{video}[/bold] \nhas new sound and is now [bold]{new_file}[/bold]')
    logger.debug(f'partial filname {partial_filename}')
    new_audio = _pathname(audio_path)
    vid_only_handle = _keep_VIDEO_only(video)
    v_n = _pathname(vid_only_handle)
    # new_file = str(out_path)
    video.unlink() # remove old one
    # building args for debug purpose only:
    ffmpeg_args = (
        ffmpeg
        .input(v_n)
        .output(new_file, vcodec='copy', acodec='pcm_s16le')
        # .output(new_file, shortest=None, vcodec='copy')
        .global_args('-i', new_audio, "-hide_banner")
        .overwrite_output()
        .get_args()
    )
    logger.debug('ffmpeg args: %s'%' '.join(ffmpeg_args))
    try: # for real now
        _, out = (
        ffmpeg
        .input(v_n)
        # .output(new_file, shortest=None, vcodec='copy')
        .output(new_file, vcodec='copy', acodec='pcm_s16le')
        .global_args('-i', new_audio, "-hide_banner")
        .overwrite_output()
        .run(capture_stderr=True)
        )
        logger.debug('ffmpeg output')
        for l in out.decode("utf-8").split('\n'):
            logger.debug(l)
    except ffmpeg.Error as e:
        print('ffmpeg.run error merging: \n\t %s + %s = %s\n'%(
            audio_path,
            video_path,
            synced_clip_file
            ))
        print(e)
        print(e.stderr.decode('UTF-8'))
        sys.exit(1)
    return partial_filename, new_file

def _sox_combine(paths) -> Path:
    """
    Combines (stacks) files referred by the list of Path into a new temporary
    files passed on return each files are stacked in a different channel, so
    len(paths) == n_channels
    """
    if len(paths) == 1: # one device only, nothing to stack
        logger.debug('one device only, nothing to stack')
        return paths[0] ########################################################
    out_file_handle = tempfile.NamedTemporaryFile(suffix='.wav',
        delete=DEL_TEMP)
    filenames = [_pathname(p) for p in paths]
    out_file_name = _pathname(out_file_handle)
    logger.debug('combining files: %s into %s'%(
        filenames,
        out_file_name))
    cbn = sox.Combiner()
    cbn.set_input_format(file_type=['wav']*len(paths))
    status = cbn.build(
        filenames,
        out_file_name,
        combine_type='merge')
    logger.debug('sox.build status: %s'%status)
    if status != True:
        print('Error, sox did not merge files in _sox_combine()')
        sys.exit(1)
    merged_duration = sox.file_info.duration(
        _pathname(out_file_handle))
    nchan = sox.file_info.channels(
        _pathname(out_file_handle)) 
    logger.debug('merged file duration %f s with %i channels '%
        (merged_duration, nchan))
    return out_file_handle

def load_New_Sound_lua_script(new_mixes):
    if LUA:
        script = DAVINCI_RESOLVE_SCRIPT_TEMPLATE_LUA
        postlude = ''
        for a,b in new_mixes:
            clip_name = Path(a).name
            postlude += '{"%s", "%s","%s"},\n'%(clip_name, a, b)
            # postlude += f"('{a}','{b}'),\n"
        postlude += '}\n\nfor _, trio in ipairs(changes) do\n'
        postlude += '    findAndReplace(trio)\n'
        postlude += 'end\n'
        # postlude += 'os.remove(pair[1])\n'
    else: # python
        script = DAVINCI_RESOLVE_SCRIPT_TEMPLATE
        postlude = '\nchanges = [\n'
        for a,b in new_mixes:
            postlude += '("%s","%s"),\n'%(a,b)
        postlude += ']\n'
        postlude += '[findAndReplace(a,b) for a, b in changes]\n\n'
    # foo = '[findAndReplace(a,b) for a, b in changes\n'
    # print('foo',foo)
    # print(postlude + foo)
    return script + postlude

def merge_new_mixes_if_any(SND_for_vid):
    # SND_for_vid is a dict of key: vid_stem val: (vid_path, SND_dir)
    changes = []
    new_mixes = []
    # two loops for meaningfull progress bar
    for vid_stem, pair in SND_for_vid.items() :
        vid_path, SND_dir = pair
        mix = get_recent_mix(SND_dir, vid_path)
        logger.debug('mix: %s'%str(mix))
        if mix != None:
            new_mixes.append((mix, vid_path))
    for mix, vid_path in rich.progress.track(new_mixes, description='merging new audio...'):
        logger.debug(f'new mix {mix} for {vid_path.name}')
        old_file, new_file = _change_audio4video(mix, vid_path)
        changes.append((old_file, new_file))
    return changes

# logger.add(sys.stdout, filter=lambda r: r["function"] == "slice_wav_for_clips")
def slice_wav_for_clips(wav_file, clips, fps):
    # return sliced audio
    N_channels = sox.file_info.channels(wav_file)
    logger.debug(f'{wav_file} has {N_channels} channels')
    tracks = yaltc.read_audio_data_from_file(wav_file, N_channels)
    audio_data = tracks.T # interleave channel samples for later slicing
    logger.debug(f'audio data shape {audio_data.shape}')
    logger.debug(f'data: {tracks}')
    logger.debug(f'tracks shape {tracks.shape}')
    # timeline_pos_fr, absolute, ie first frame of whole project is 0
    # in frame number
    timeline_pos_fr = [int(round((cl.timeline_pos - ONE_HR_START)*fps))
                                                for cl in clips]
    logger.debug(f'timeline_pos_fr {timeline_pos_fr}')
    # left_trims in frame units
    left_trims = [rint((cl.in_time - cl.start_time)*fps) for cl in clips]
    logger.debug(f'left_trims: {left_trims} frames')
    # sampling frequency, samples per second
    samples_per_second = sox.file_info.sample_rate(wav_file)
    # number of audio samples per frames, 
    samples_per_frame = samples_per_second/fps
    logger.debug(f'there are {samples_per_frame} audio samples for each frame')
    # in counts of audio samples, As are starts of audio_data slices,
    # Bs are end of slices (sample # excluded)
    As = [rint((tmlp - Ltr)*samples_per_frame) for tmlp, Ltr
                                    in zip(timeline_pos_fr, left_trims)]
    Bs = [rint((cl.whole_duration*samples_per_second + A)) for cl, A
                                        in zip(clips, As)]
    logger.debug(f'As: {As} Bs: {Bs}')
    ABs = list(zip(As,Bs))
    logger.debug(f'ABs {ABs}, audio samples')
    audio_slices = [audio_data[A:B] for A, B in zip(As, Bs)]
    logger.debug(f'audio_slices lengths {[len(s) for s in audio_slices]}')
    if len(audio_slices[0]) == 0:
        logger.debug(f'first slice had negative start, must pad it')
        n_null_samples = rint(left_trims[0]*samples_per_frame)*N_channels
        silence = np.zeros(n_null_samples).reshape(-1, N_channels)
        logger.debug(f'silence: {silence}')
        oldA, oldB = ABs[0]
        newA = oldA + len(silence) # should be 0 :-)
        newB = oldB + len(silence)
        logger.debug(f'newA, newB: {newA, newB}')
        padded_audio_data = np.concatenate([silence, audio_data])
        first_slice = padded_audio_data[newA:newB]
        audio_slices = [first_slice] + audio_slices[1:]
    # check if last clip has right trim, if so, should zero-pad the slice
    lcl = clips[-1]
    w, i, s, c = lcl.whole_duration, lcl.in_time, lcl.start_time, lcl.cut_duration
    right_trim_last = w - i + s - c
    logger.debug(f'right_trim_last: {right_trim_last} sec')
    if right_trim_last > 0:
        # add zeros to last slice
        n_null_samples = rint(right_trim_last*samples_per_second)*N_channels
        silence = np.zeros(n_null_samples).reshape(-1, N_channels)
        new_last_slice = np.concatenate([audio_slices[-1], silence]) 
        audio_slices = audio_slices[:-1] + [new_last_slice]
    slices_durations = [rint(len(aslice)/samples_per_frame)
                                    for aslice in audio_slices]
    logger.debug(f'slices_durations {slices_durations}')
    clip_durations = [rint(cl.whole_duration*fps) for cl in clips]
    logger.debug(f'clip_durations: {clip_durations}')
    same = [a==b for a,b in list(zip(slices_durations, clip_durations))]
    logger.debug(f'same: {same}')
    ok = all(same)
    if not ok:
        for clip, slice_duration in zip(clips, slices_durations):
            print(f'clip "{clip.name}", duration: {rint(clip.whole_duration*fps)} slice duration: {slice_duration} frames')
        raise Exception("Error: audio slices don't have the same duration than video clips. Bye.")
    return audio_slices, samples_per_second

# logger.add(sys.stdout, filter=lambda r: r["function"] == "go")
def go(mode, otio_path, movie_path, wav_path):
    raw_root, synced_root, snd_root, proxies = mamconf.get_proj(False)
    match mode:
        case Modes.INTRACLIP:
            print(f'Intraclip sound editing: will search for new mixes in {snd_root}')
        case Modes.INTERCLIP_ALL:
            print(f'Interclip sound editing: will split whole soundtrack {wav_path} among all clips.')
        case Modes.INTERCLIP_SOME:
            print(f'Interclip sound editing: will split soundtrack extarct {wav_path} among some clips.')
    logger.debug(f'mode is {mode}')
    proj_name = Path(raw_root).name
    synced_project = Path(synced_root)/proj_name
    project_sounds = Path(snd_root)/proj_name
    # SND_for_vid is a dict of (key: vid; value: (vpath, SND))
    # where vid is video stem without version and SND is absolute pathlib.Path
    # e.g.:
    # vid = 'canon24fps01'
    # vpath = '/Users/.../canon24fps01vB.mov' complete vid path
    # SND = '/Users/.../canon24fps01_SND' <- directory where mix is could be saved
    SND_for_vid = find_SND_vids_pairs_in_dual_dir(synced_project, project_sounds)
    logger.debug(f'SND_for_vid {pformat(SND_for_vid)}')
    if mode == Modes.INTERCLIP_ALL:
        fps, clips =mamreap.read_OTIO_file(otio_path)
        wav_length = sox.file_info.duration(wav_path)
        last_clip = clips[-1]
        otio_duration = last_clip.timeline_pos + last_clip.cut_duration - 3600
        if not np.isclose(wav_length, otio_duration):
            print(f'Error, mix wav file duration {wav_length} does not match timeline duration {otio_duration} seconds. Bye')
            print(wav_path)
            sys.exit(0)
        logger.debug(f' mode is INTERCLIP_ALL, otio has {fps} fps')
        audio_slices, samples_per_second = slice_wav_for_clips(wav_path, clips, fps)
        slices_clips = zip(audio_slices, clips)
        # breakpoint()
        for aslc, clip in slices_clips:
            stem = _vid_stem(clip.path)
            wav_name = f'{stem}_mix.wav'
            _, directory = SND_for_vid[stem]
            wav_name = directory / wav_name
            wrt_wav(wav_name, int(samples_per_second), aslc.astype(np.int16))
            # logger.debug(f'audio_slice for clip {clip.name}: {aslc.shape} {aslc}')
            logger.debug(f'written in {wav_name}')
        # Modes.INTERCLIP_ALL check if length wav == length otio
    changes = merge_new_mixes_if_any(SND_for_vid)
    # breakpoint()
    if len(changes) == 0:
        print('No new mix.')
        sys.exit(0)
    else:
        print('Here are the clips with new sound track: ', end='')
        for old_file, new_file in changes[:-1]:
            print(f'"{_vid_stem(new_file)}", ', end='')
    old_file, new_file = changes[-1]
    print(f'"{_vid_stem(new_file)}".')            
    logger.debug(f'changes {pformat(changes)}')
    script = load_New_Sound_lua_script(changes)
    script_path = Path(DAVINCI_RESOLVE_SCRIPT_LOCATION)/'Load New Sound.lua'
    # script += f'os.remove("{script_path}")\n' # doesnt work
    with open(script_path, 'w') as fh:
        fh.write(script)
    print(f'Wrote new Lua script: run it in Resolve under Workspace/Scripts/{script_path.stem};')
    print(f'script full path: "{script_path}".')
    # print(script)

# logger.add(sys.stdout, filter=lambda r: r["function"] == "called_from_cli")
def called_from_cli():
    # MAM mode always
    logger.debug('CLI')
    mode, otio_path, movie_path, wav_path = parse_args_for_mode_and_files()
    go(mode, otio_path, movie_path, wav_path)

if __name__ == '__main__':
    called_from_cli()    
