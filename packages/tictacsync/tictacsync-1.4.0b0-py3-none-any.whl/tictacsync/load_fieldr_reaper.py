import json, pathlib, itertools, os, re, ffmpeg
import argparse, platformdirs, configparser, sys
from loguru import logger
from pprint import pformat
from dataclasses import dataclass
from rich import print

try:
    from . import mamconf
except:
    import mamconf

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

logger.level("DEBUG", color="<yellow>")
logger.add(sys.stdout, level="DEBUG")
logger.remove()

def parse_and_check_arguments():
    # parses directories from command arguments
    # check for consistencies and warn user and exits,
    # returns parser.parse_args()
    descr = "Parse the submitted OTIO timeline and build a Reaper Script to load the corresponding ISO files from SNDROOT (see mamconf --show)"
    parser = argparse.ArgumentParser(description=descr) 
    parser.add_argument(
                "a_file_argument",
                type=str,
                nargs=1,
                help="path of timeline saved under OTIO format"
                )
    parser.add_argument('--interval',
                    dest='interval',
                    nargs=2,
                    help="One or two timecodes, space seperated, delimiting the zone to process (if not specified the whole timeline is processed)")
    args = parser.parse_args()
    logger.debug('args %s'%args)
    return args

@dataclass
class Clip:
    # all time in seconds
    start_time: float # the start time of the clip in
    in_time: float # time of 'in' point, relative to clip start_time
    cut_duration: float
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
        In, the "in time"
        cd, the cut duration
        wl, the whole length of the unedited clip
        the clip file path (string)
        name (string)
    NB: the position on the global timeline is not stored but latter computed from summing cut times
    """
    def _float_time(json_rationaltime):
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
    clip_stem = pathlib.Path(clip.path).stem
    logger.debug(f'clip_stem {clip_stem}')
    m = re.match('(.*)v([AB]*)', clip_stem)
    logger.debug(f'{clip_stem} match (.*)v([AB]*) { m.groups() if m != None else None}')
    if m != None:
        clip_stem = m.groups()[0]
    # /MyBigMovie/day01/leftCAM/card01/canon24fps01_SND -> canon24fps01_SND
    names_only = [p.name for p in SND_dirs]
    logger.debug(f'names-only {pformat(names_only)}')
    clip_stem_SND = f'{clip_stem}_SND'
    if clip_stem_SND in names_only:
        where = names_only.index(clip_stem_SND)
    else:
        print(f'Error: OTIO file contains clip not in SYNCEDROOT: {clip_stem} (check with mamconf --show)')
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
    logger.debug(f'clips: {pformat(clips)}')
    # compute each clip global timeline position
    clip_starts = [0] + list(itertools.accumulate([cl.cut_duration for cl in clips]))[:-1]
    # Reaper can't handle negative item position (for the trimmed part)
    # so starts at 1:00:00
    clip_starts = [t + 3600 for t in clip_starts]
    logger.debug(f'clip_starts: {clip_starts}')
    for time, clip in zip(clip_starts, clips):
        clip.timeline_pos = time
    return int(oti['global_start_time']['rate']), clips

def reaper_save_action(wav_destination):
    return f"""reaper.GetSetProjectInfo_String(0, "RENDER_FILE","{wav_destination.parent}",true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN","{wav_destination.name}",true)
reaper.SNM_SetIntConfigVar("projintmix", 4)
reaper.Main_OnCommand(40015, 0)
"""

# logger.add(sys.stdout, filter=lambda r: r["function"] == "complete_clip_path")
def complete_clip_path(clip_stem, synced_proj):
    match = []
    for (root,dirs,files) in os.walk(synced_proj):
        for f in files:
            p = pathlib.Path(root)/f
            if p.is_symlink() or p.suffix == '.reapeaks':
                continue
            # logger.debug(f'{f}')
            if clip_stem in f.split('.')[0]: # match XYZvA.mov
                match.append(p)
    logger.debug(f'matches {match}')
    if len(match) > 1:
        print(f'Warning, some filenames collide {pformat(match)}, Bye.')
        sys.exit(0)
    if len(match) == 0:
        print(f"Error, didn't find any clip containing *{clip_stem}*. Bye.")
        sys.exit(0)
    return match[0]

# logger.add(sys.stdout, filter=lambda r: r["function"] == "main")
def main():
    def _where(a,x):
        # find in which clip time x (in seconds) does fall.
        n = 0
        while n<len(a):
            if a[n].timeline_pos > x:
                break
            else:
                n += 1
        return n-1
    raw_root, synced_root, snd_root, proxies = mamconf.get_proj(False)
    proj_name = pathlib.Path(raw_root).stem
    synced_proj = pathlib.Path(synced_root)/proj_name
    logger.debug(f'proj_name {proj_name}')
    logger.debug(f'will search {snd_root} for ISOs')
    all_SNDROOT_dirs = [pathlib.Path(f) for f in get_SND_dirs(snd_root)]
    # keep only XYZ_SND dirs
    SND_dirs = [p for p in all_SNDROOT_dirs if p.name[-4:] == '_SND']
    logger.debug(f'SND_dirs {pformat(SND_dirs)}')
    args = parse_and_check_arguments()
    file_arg = pathlib.Path(args.a_file_argument[0])
    # check if its intraclip or interclip sound edit
    # if otio file then interclip
    if file_arg.suffix == '.otio':
        logger.debug('interclip sound edit, filling up clips')
        _, clips = read_OTIO_file(file_arg)
        [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
    else:
        logger.debug('intraclip sound edit, clips will have one clip')
        # traverse synced_root to find clip path
        clip_path = complete_clip_path(file_arg.stem, synced_proj)
        probe = ffmpeg.probe(clip_path)
        duration = float(probe['format']['duration'])
        clips = [Clip(
                    start_time=0,
                    in_time=0,
                    cut_duration=duration,
                    whole_duration=duration,
                    name=file_arg.stem,
                    path=clip_path,
                    timeline_pos=3600,
                    ISOdir='')]
        [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
        print(f'For video clip \n{clip_path}\nfound audio in\n{clips[0].ISOdir}')
    logger.debug(f'clips with found ISOdir: {pformat(clips)}')
    lua_clips = gen_lua_table(clips)
    logger.debug(f'lua_clips {lua_clips}')
    # title = "Load cut26_MyBigMovie" or "Load clip026_MyBigMovie"
    arg_name = pathlib.Path(args.a_file_argument[0]).stem
    title = f'Load {arg_name}_{pathlib.Path(raw_root).stem}'
    # script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'{title}.lua'
    script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'Load Clip Audio.lua'
    # script += f'os.remove("{script_path}")\n' # doesnt work
    Lua_script_pre, _ , Lua_script_post = REAPER_LUA_CODE.split('--cut here--')
    script = Lua_script_pre + 'clips=' + lua_clips + Lua_script_post
    with open(script_path, 'w') as fh:
        fh.write(script)
    print(f'Wrote script {script_path}')
    if file_arg.suffix != 'otio':
        # build "Set rendering for" action
        destination = pathlib.Path(clips[0].ISOdir)/'mix.wav'
        logger.debug(f'will build set rendering for {arg_name} with dest: {destination}')
        render_action = reaper_save_action(destination)
        logger.debug(f'clip\n{render_action}')
        # script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'Set rendering for {arg_name}.lua'
        script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'Render Clip Audio.lua'
        with open(script_path, 'w') as fh:
            fh.write(render_action)
        print(f'Wrote script {script_path}')


if __name__ == '__main__':
    main()

