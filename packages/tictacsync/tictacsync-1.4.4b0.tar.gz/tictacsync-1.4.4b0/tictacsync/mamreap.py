import json, pathlib, itertools, os, re, ffmpeg, shutil, time
import argparse, platformdirs, configparser, sys
from loguru import logger
from pprint import pformat
from dataclasses import dataclass
from rich import print
from enum import Enum
from rich.progress import Progress

# send-to-sound DSC085 -> one clip only, find the ISOs, load the clip
# send-to-sound cut27.otio -> whole project
# send-to-sound cut27.otio cut27.mov
#     cut27.mov has TC + duration -> can find clips in otio...
#     place cut27.mov according to its TC
#     produce a cut27mix.wav saved in SNDROOT/postprod
# three modes: one clip; some clips; all clips



try:
    from . import mamconf
    from . import mamdav
except:
    import mamconf
    import mamdav

dev = 'Cockos Incorporated'
app ='REAPER'
REAPER_SCRIPT_LOCATION = pathlib.Path(platformdirs.user_data_dir(app, dev)) / 'Scripts' / 'Atomic'
REAPER_LUA_CODE = """reaper.Main_OnCommand(40577, 0) -- lock left/right move
reaper.Main_OnCommand(40569, 0) -- lock enabled
local function placeWavsBeginingAtTrack(clip, start_idx)
  for i, file in ipairs(clip.files) do
    local track_idx = start_idx + i - 1
    local track = reaper.GetTrack(nil,track_idx-1)
    reaper.SetOnlyTrackSelected(track)
    local left_trim = clip.in_time - clip.start_time
    local where = clip.timeline_pos - left_trim
    reaper.SetEditCurPos(where, false, false)
    reaper.InsertMedia(file, 0 )
    local item_cnt = reaper.CountTrackMediaItems( track )
    local item = reaper.GetTrackMediaItem( track, item_cnt-1 )
    local take = reaper.GetTake(item, 0)
    -- reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", clip.name, true)
    local pos = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
    reaper.BR_SetItemEdges(item, clip.timeline_pos, clip.timeline_pos + clip.cut_duration)
    reaper.SetMediaItemInfo_Value(item, "C_LOCK", 2)
  end
end

--cut here--

sample of the clips nested table (this will be discarded)
each clip has an EDL info table plus a sequence of ISO files:

clips =
{
{
    name="canon24fps01.MOV", start_time=7.25, in_time=21.125, cut_duration=6.875, timeline_pos=3600,
    files=
        {
        "/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps01_SND/ISOfiles/Alice_canon24fps01.wav",
        "/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps01_SND/ISOfiles/Bob_canon24fps01.wav"
        }
},
{name="DSC_8063.MOV", start_time=0.0, in_time=5.0, cut_duration=20.25, timeline_pos=3606.875,
files={"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/rightCAM/ROLL01/DSC_8063_SND/ISOfiles/Alice_DSC_8063.wav",
"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/rightCAM/ROLL01/DSC_8063_SND/ISOfiles/Bob_DSC_8063.wav"}},
{name="canon24fps02.MOV", start_time=35.166666666666664, in_time=35.166666666666664, cut_duration=20.541666666666668, timeline_pos=3627.125, files={"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps02_SND/ISOfiles/Alice_canon24fps02.wav",
"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps02_SND/ISOfiles/Bob_canon24fps02.wav"}}
}

--cut here--
-- make room fro the tracks to come
amplitude_top = 0
amplitude_bottom = 0
for i_clip, cl in pairs(clips) do
  if i_clip%2 ~= 1 then
    amplitude_top = math.max(amplitude_top, #cl.files)
  else
    amplitude_bottom = math.max(amplitude_bottom, #cl.files)
  end
end
for i = 1 , amplitude_top + amplitude_bottom + 1 do
  reaper.InsertTrackAtIndex( -1, false ) -- at end
end
track_count = reaper.CountTracks(0)
-- ISOs will be up and down the base_track index
base_track = track_count - amplitude_bottom
for iclip, clip in ipairs(clips) do
  start_track_number = base_track
  -- alternating even/odd, odd=below base_track 
  if iclip%2 == 0 then -- above base_track, start higher
    start_track_number = base_track - #clip.files
  end
  placeWavsBeginingAtTrack(clip, start_track_number)
  if #clips > 1 then -- interclips editing
    reaper.AddProjectMarker(0, false, clip.timeline_pos, 0, '', -1)
  end
end
reaper.SetEditCurPos(3600, false, false)
reaper.Main_OnCommand(40151, 0)
if #clips > 1 then -- interclips editing
-- last marker at the end
  last_clip = clips[#clips]
  reaper.AddProjectMarker(0, false, last_clip.timeline_pos + last_clip.cut_duration, 0, '', -1)
end

"""
v_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp""".split()



logger.level("DEBUG", color="<yellow>")
logger.add(sys.stdout, level="DEBUG")
logger.remove()

# class Modes(Enum):
#     INTRACLIP = 1 # send-to-sound --clip DSC085 -> find the ISOs, load the clip in Reaper
#     INTERCLIP_SOME = 2 # send-to-sound cut27.otio cut27.mov
#             # cut27.mov has TC + duration -> can find clips in otio...
#             # place cut27.mov according to its TC
#             # Reaper will then produces a cut27mix.wav saved in SNDROOT/postprod
#     INTERCLIP_ALL = 3 # send-to-sound cut27.otio -> whole project

# logger.add(sys.stdout, filter=lambda r: r["function"] == "parse_args_get_mode")
def parse_args_get_mode():
    """
    parse args and determine which one of modes is used: INTRACLIP, INTERCLIP_SOME or
    INTERCLIP_ALL.
    Returns a 4-tuple: (mode, clip_argument, otio_file, render_file);
    mode is of type mamdav.Modes(Enum); each of clip_argument, otio_file and render_file is None
    if unset on the command line and of type str if set.
    """

    descr = """Take the video clip (-c option) or parse the submitted OTIO timeline
    (-a and -p options) to build a Reaper Script which loads the corresponding
    ISO files from SNDROOT (see mamconf --show)."""
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('-e',
                    action='store_true',
                    help="exit on completion (don't wait for the wav mix to be rendered by Reaper)")
    parser.add_argument('-c',
                    dest='the_clip',
                    nargs=1,
                    help="send only this specified clip to Reaper (partial name is OK)")
    parser.add_argument('-a',
                    dest='all',
                    nargs='*',
                    help="all the timeline will be sent and edited in Reaper")
    parser.add_argument('-p',
                    dest='partial',
                    nargs='*',
                    help="only a timeline selected region will be edited in Reaper")
    args = parser.parse_args()
    logger.debug('args %s'%args)
    if args.the_clip != None:
        if len(args.the_clip) > 1:
            print('Error: -c <A_CLIP> option should be used alone without any other argument. Bye.')
            sys.exit(0)
        else:
            # e.g. send-to-sound DSC087
            # return: mode, clip_argument, otio_file, render
            mode, clip_argument, otio_file, render_file = \
                (mamdav.Modes.INTRACLIP, *args.the_clip, None, None)
            exit = args.e
            logger.debug('mode, clip_argument, otio_file, render_file, exit:')
            logger.debug(f'{str(mode)}, { clip_argument}, {otio_file}, {render_file}, {exit}.')
            return mode, clip_argument, otio_file, render_file, exit #################
    def _is_otio(f):
        components = f.split('.')
        if len(components) == 1:
            return False
        return components[-1].lower() == 'otio'
    if args.all != None:
        otio_and_render = args.all
        if args.partial != None:
            print('Error: -a and -p are mutually exclusive, bye.')
            sys.exit(0)
    if args.partial != None:
        otio_and_render = args.partial
        if args.all != None:
            print('Error: -a and -p are mutually exclusive, bye.')
            sys.exit(0)
    if len(otio_and_render) > 2:
        print(f'Error: no more than two files are needed, bye.')
        sys.exit(0)
    otio_candidate = [f for f in otio_and_render if _is_otio(f)]
    logger.debug(f'otio_candidate {otio_candidate}')
    if len(otio_candidate) == 0:
        print('Error: an OTIO file (or a -c argument) is needed. Bye.')
        sys.exit(0)
    if len(otio_candidate) > 1:
        print(f'Error: one OTIO file is needed, not {len(otio_candidate)}. Bye.')
        sys.exit(0)
    otio = otio_candidate[0]
    if len(otio_and_render) == 1:
        # e.g.: send-to-sound cut27.otio
        # return: mode, clip_argument, otio_file, render
        mode, clip_argument, otio_file, render_file = \
            (mamdav.Modes.INTERCLIP_ALL, None, otio, None)
        exit = args.e
        logger.debug('mode, clip_argument, otio_file, render_file, exit:')
        logger.debug(f'{str(mode)}, { clip_argument}, {otio_file}, {render_file}, {exit}.')
        return mode, clip_argument, otio_file, render_file, exit #####################
    render = [f for f in otio_and_render if f != otio][0]
    if render.split('.')[-1].lower() not in v_file_extensions:
        print(f'Error: "{render}" does not have a video file extension, bye.')
        sys.exit(0)
    # e.g.: send-to-sound cut27.otio cut27.mov
    # return: mode, clip_argument, otio_file, render
    mode, clip_argument, otio_file, render_file = \
        (mamdav.Modes.INTERCLIP_SOME, None, otio, render)
    exit = args.e
    logger.debug('mode, clip_argument, otio_file, render_file, exit:')
    logger.debug(f'{str(mode)}, { clip_argument}, {otio_file}, {render_file}, {exit}.')
    return mode, clip_argument, otio_file, render_file, exit #########################

@dataclass
class Clip:
    # all time in seconds
    start_time: float # the start time of the clip, != 0 if metadata TC
    in_time: float # time of 'in' point, if in_time == start_time, no left trim
    cut_duration: float # with this value, right trim is detemined, if needed
    whole_duration: float # unedited clip duration
    name: str #
    path: str # path of clip
    timeline_pos: float # when on the timeline the clip starts
    ISOdir: None # folder of ISO files for clip

def clip_info_from_json(jsoncl):
    """
    parse data from an OTIO json Clip
    https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-serialized-schema.html#clip-2
    returns a list composed of (all times are in seconds):
        st, start time (from clip metadata TC) 
        In, the "in time", if in_time == start_time, no left trim
        cd, the cut duration
        wl, the whole length of the unedited clip
        the clip file path (string)
        name (string)
    NB: Clip.timeline_pos (the position on the global timeline) is not set here but latter computed from summing cut times
    """
    def _float_time(json_rationaltime):
        # returns a time in seconds (float)
        return json_rationaltime['value']/json_rationaltime['rate']
    av_range = jsoncl['media_references']['DEFAULT_MEDIA']['available_range']
    src_rg = jsoncl['source_range']
    st = av_range['start_time']
    In = src_rg['start_time']
    cd = src_rg['duration']
    wl = av_range['duration']
    path = jsoncl['media_references']['DEFAULT_MEDIA']['target_url']
    name = jsoncl['media_references']['DEFAULT_MEDIA']['name']
    return Clip(*[_float_time(t) for t in [st, In, cd, wl,]] + \
                    [name, path, 0, None])

def get_SND_dirs(snd_root):
    # returns all directories found under snd_root
    def _searchDirectory(cwd,searchResults):
        dirs = os.listdir(cwd)
        for dir in dirs:
            fullpath = os.path.join(cwd,dir)
            if os.path.isdir(fullpath):
                searchResults.append(fullpath)
                _searchDirectory(fullpath,searchResults)
    searchResults = []
    _searchDirectory(snd_root,searchResults)
    return searchResults

# logger.add(sys.stdout, filter=lambda r: r["function"] == "find_and_set_ISO_dir")
def find_and_set_ISO_dir(clip, SND_dirs):
    """
    SND_dirs contains all the *_SND directories found in snd_root.
    This fct finds out which one corresponds to the clip
    and sets the found path to clip.ISOdir.
    Returns nothing.
    """
    clip_argument = pathlib.Path(clip.path).stem
    logger.debug(f'clip_argument {clip_argument}')
    m = re.match(r'(.*)_v(\w{32})', clip_argument) # 
    logger.debug(f'{clip_argument} match (.*)v([AB]*) { m.groups() if m != None else None}')
    if m != None:
        clip_argument = m.groups()[0]
    # /MyBigMovie/day01/leftCAM/card01/canon24fps01_SND -> canon24fps01_SND
    names_only = [p.name for p in SND_dirs]
    logger.debug(f'names-only {pformat(names_only)}')
    clip_stem_SND = f'{clip_argument}_SND'
    if clip_stem_SND in names_only:
        where = names_only.index(clip_stem_SND)
    else:
        print(f'Error: OTIO file contains clip not in SYNCEDROOT: {clip_argument} (check with mamconf --show)')
        sys.exit(0)
    complete_path = SND_dirs[where]
    logger.debug(f'found {complete_path}')
    clip.ISOdir = str(complete_path)

def gen_lua_table(clips):
    # returns a string defining a lua nested table
    # top level: a sequence of clips
    # a clip has keys: name, start_time, in_time, cut_duration, timeline_pos, files
    # clip.files is a sequence of ISO wav files
    def _list_ISO(dir):
        iso_dir = pathlib.Path(dir)/'ISOfiles'
        ISOs = [f for f in iso_dir.iterdir() if f.suffix.lower() == '.wav']
        # ISOs = [f for f in ISOs if f.name[:2] != 'tc'] # no timecode
        logger.debug(f'ISOs {ISOs}')
        sequence = '{'
        for file in ISOs:
            sequence += f'"{file}",\n'
        sequence += '}'
        return sequence
    lua_clips = '{'
    for cl in clips:
        ISOs = _list_ISO(cl.ISOdir)
        # logger.debug(f'sequence {ISOs}')
        clip_table = f'{{name="{cl.name}", start_time={cl.start_time}, in_time={cl.in_time}, cut_duration={cl.cut_duration}, timeline_pos={cl.timeline_pos}, files={ISOs}}}'
        lua_clips += f'{clip_table},\n'
        logger.debug(f'clip_table {clip_table}')
    lua_clips += '}'
    return lua_clips
    
# logger.add(sys.stdout, filter=lambda r: r["function"] == "read_OTIO_file")
def read_OTIO_file(f):
    """
    returns framerate and a list of Clip instances parsed from
    the OTIO file passed as (string) argument f;
    warns and exists if more than one video track.
    """
    with open(f) as fh:
        oti = json.load(fh)
    video_tracks = [tr for tr in oti['tracks']['children'] if tr['kind'] == 'Video']
    if len(video_tracks) > 1:
        print(f"Can only process timeline with one video track, this one has {len(video_tracks)}. Bye.")
        sys.exit(0)
    video_track = video_tracks[0]
    clips = [clip_info_from_json(jscl) for jscl in video_track['children']]
    # compute each clip global timeline position
    clip_starts = [0] + list(itertools.accumulate([cl.cut_duration for cl in clips]))[:-1]
    # Reaper can't handle negative item position (for the trimmed part)
    # so starts at 1:00:00
    clip_starts = [t + 3600 for t in clip_starts]
    logger.debug(f'clip_starts: {clip_starts}')
    for time, clip in zip(clip_starts, clips):
        clip.timeline_pos = time
    logger.debug(f'clips: {pformat(clips)}')
    return int(oti['global_start_time']['rate']), clips

def build_reaper_render_action(wav_destination):
    directory = wav_destination.absolute().parent
    return f"""reaper.GetSetProjectInfo_String(0, "RENDER_FILE","{directory}",true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN","{wav_destination.name}",true)
reaper.SNM_SetIntConfigVar("projintmix", 4)
reaper.Main_OnCommand(40015, 0)
"""
# logger.add(sys.stdout, filter=lambda r: r["function"] == "complete_clip_path")
def complete_clip_path(clip_argument, synced_proj):
    match = []
    for (root,dirs,files) in os.walk(synced_proj):
        for f in files:
            p = pathlib.Path(root)/f
            if p.is_symlink() or p.suffix == '.reapeaks':
                continue
            # logger.debug(f'{f}')
            if clip_argument in f.split('.')[0]: # match XYZvA.mov
                match.append(p)
    logger.debug(f'matches {match}')
    if len(match) > 1:
        print(f'Warning, some filenames collide:')
        [print(m) for m in match]
        print('Bye.')
        sys.exit(0)
    if len(match) == 0:
        print(f"Error, didn't find any clip containing *{clip_argument}*. Bye.")
        sys.exit(0)
    return match[0]

# logger.add(sys.stdout, filter=lambda r: r["function"] == "main")
def main():
    mode, clip_argument, otio_file, render, exit = parse_args_get_mode() 
    # def _where(a,x):
    #     # find in which clip time x (in seconds) does fall.
    #     n = 0
    #     while n<len(a):
    #         if a[n].timeline_pos > x:
    #             break
    #         else:
    #             n += 1
    #     return n-1
    raw_root, synced_root, snd_root, proxies = mamconf.get_proj(False)
    proj_name = pathlib.Path(raw_root).stem
    synced_proj = pathlib.Path(synced_root)/proj_name
    logger.debug(f'proj_name {proj_name}')
    logger.debug(f'will search {snd_root} for ISOs')
    all_SNDROOT_dirs = [pathlib.Path(f) for f in get_SND_dirs(snd_root)]
    # keep only XYZ_SND dirs
    SND_dirs = [p for p in all_SNDROOT_dirs if p.name[-4:] == '_SND']
    logger.debug(f'SND_dirs {pformat(SND_dirs)}')
    match mode:
        case mamdav.Modes.INTRACLIP:
            # e.g.: send-to-sound DSC087
            logger.debug('Modes.INTRACLIP, intraclip sound edit, clips will have one clip')
            # traverse synced_root to find clip path
            clip_path = complete_clip_path(clip_argument, synced_proj)
            clip_stem = clip_path.stem
            probe = ffmpeg.probe(clip_path)
            duration = float(probe['format']['duration'])
            clips = [Clip(
                        start_time=0,
                        in_time=0,
                        cut_duration=duration,
                        whole_duration=duration,
                        name=clip_argument,
                        path=clip_path,
                        timeline_pos=3600,
                        ISOdir='')]
            [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
            print(f'For video clip: \n{clip_path}\nfound audio in:\n{clips[0].ISOdir}')
        case mamdav.Modes.INTERCLIP_SOME:
            # [TODO]
            # e.g.: mamreap -p cut27.otio cut27.mov
            pass
        case mamdav.Modes.INTERCLIP_ALL:
            # e.g.: send-to-sound cut27.otio
            logger.debug('Modes.INTERCLIP_ALL, interclip sound edit, filling up ALL clips')
            _, clips = read_OTIO_file(otio_file)
            [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
    logger.debug(f'clips with found ISOdir: {pformat(clips)}')
    lua_clips = gen_lua_table(clips)
    logger.debug(f'lua_clips {lua_clips}')
    # title = "Load MyBigMovie Audio.lua" either Modes
    title = f'Load {pathlib.Path(raw_root).name} Audio'
    script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'{title}.lua'
    Lua_script_pre, _ , Lua_script_post = REAPER_LUA_CODE.split('--cut here--')
    script = Lua_script_pre + 'clips=' + lua_clips + Lua_script_post
    with open(script_path, 'w') as fh:
        fh.write(script)
    print(f'Wrote ReaScripts "{script_path.stem}"', end=' ')
    if mode == mamdav.Modes.INTRACLIP:
        render_destination = pathlib.Path(clips[0].ISOdir)/f'{clip_stem}_mix.wav'
    else:
        logger.debug('render for mode all clips')
        op = pathlib.Path(otio_file)
        render_destination = op.parent/f'{op.stem}_mix.wav'
        logger.debug(f'render destination {render_destination}')
    logger.debug(f'will build rendering clip with dest: {render_destination}')
    lua_code = build_reaper_render_action(render_destination)
    if render_destination.exists():
        render_destination.unlink()
    logger.debug(f'clip\n{lua_code}')
    script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'Render Movie Audio.lua'
    with open(script_path, 'w') as fh:
        fh.write(lua_code)
    print(f'and "{script_path.stem}"')
    print(f'Reaper will render audio to "{render_destination.absolute()}"')
    if mode in [mamdav.Modes.INTERCLIP_ALL, mamdav.Modes.INTERCLIP_SOME]:
        print(f'Warning: once saved, "{render_destination.name}" wont be of any use if not paired with "{op.name}", so keep them in the same directory.')
    if not exit:
        # wait for mix and lauch mamdav
        print('Go editing in Reaper...')
        with Progress(transient=True) as progress:
            task = progress.add_task(f"[green]Waiting for {render_destination.name}...", total=None)
            while not render_destination.exists():
                time.sleep(5)
            progress.stop()
        time.sleep(3) # finishing writing?
        print(f'saw {render_destination.name}: ')
        # print('go mamdav!')
        wav_path = render_destination
        movie_path = None
        otio_path = op
        mamdav.go(mode, otio_path, movie_path, wav_path)



if __name__ == '__main__':
    main()

