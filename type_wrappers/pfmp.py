from ..itype_wrapper import ITypeWrapper, ITypeRootWrapper
from ..properties import ElementProperty


class _RenderSettings(ITypeWrapper):
    _prop: ElementProperty

    @property
    def height(self):
        return self._prop['height']

    @property
    def width(self):
        return self._prop['width']

    @property
    def pre_calculate_light(self):
        return self._prop['preCalculateLight']

    @property
    def camera_type(self):
        return self._prop['cameraType']

    @property
    def panorama_type(self):
        return self._prop['panoramaType']

    @property
    def panorama_range(self):
        return self._prop['panoramaRange']

    @property
    def render_world(self):
        return self._prop['renderWorld']

    @property
    def device_type(self):
        return self._prop['deviceType']

    @property
    def stereoscopic(self):
        return self._prop['stereoscopic']

    @property
    def preview_quality(self):
        return self._prop['previewQuality']

    @property
    def progressive(self):
        return self._prop['progressive']

    @property
    def progressive_refinement_enabled(self):
        return self._prop['progressiveRefinementEnabled']

    @property
    def samples(self):
        return self._prop['samples']

    @property
    def denoise_mode(self):
        return self._prop['denoiseMode']

    @property
    def viewport_mode(self):
        return self._prop['viewportMode']

    @property
    def max_transparency_bounces(self):
        return self._prop['maxTransparencyBounces']

    @property
    def exposure(self):
        return self._prop['exposure']

    @property
    def light_intensity_factor(self):
        return self._prop['lightIntensityFactor']

    @property
    def emission_strength(self):
        return self._prop['emissionStrength']

    @property
    def output_format(self):
        return self._prop['outputFormat']

    @property
    def number_of_frames(self):
        return self._prop['numberOfFrames']

    @property
    def render_engine(self):
        return self._prop['renderEngine']

    @property
    def color_transform(self):
        return self._prop['colorTransform']

    @property
    def frame_rate(self):
        return self._prop['frameRate']

    @property
    def color_transform_look(self):
        return self._prop['colorTransformLook']

    @property
    def render_game_objects(self):
        return self._prop['renderGameObjects']

    @property
    def transparent_sky(self):
        return self._prop['transparentSky']

    @property
    def pvs_culling_enabled(self):
        return self._prop['pvsCullingEnabled']

    @property
    def camera_frustum_culling_enabled(self):
        return self._prop['cameraFrustumCullingEnabled']

    @property
    def render_player(self):
        return self._prop['renderPlayer']

    @property
    def mode(self):
        return self._prop['mode']

    @property
    def preset(self):
        return self._prop['preset']


class _SessionSettings(ITypeWrapper):
    _prop: ElementProperty

    @property
    def playhead_offset(self):
        return self._prop['playheadOffset']

    @property
    def render_settings(self):
        return _RenderSettings(self._prop['renderSettings'])


class _TimeFrame(ITypeWrapper):
    _prop: ElementProperty

    @property
    def start(self):
        return self._prop['start']

    @property
    def duration(self):
        return self._prop['duration']

    @property
    def offset(self):
        return self._prop['offset']

    @property
    def scale(self):
        return self._prop['scale']


class _Scene(ITypeWrapper):
    _prop: ElementProperty

    @property
    def unique_id(self):
        return self._prop['uniqueId']

    @property
    def actors(self):
        return self._prop['actors']

    @property
    def transform(self):
        return self._prop['transform']

    @property
    def name(self):
        return self._prop['name']

    @property
    def visible(self):
        return self._prop['visible']

    @property
    def groups(self):
        return self._prop['groups']


class _OverlayClip(ITypeWrapper):
    _prop: ElementProperty


class _FilmClip(ITypeWrapper):
    _prop: ElementProperty


class _AudioClip(ITypeWrapper):
    _prop: ElementProperty


class _Track(ITypeWrapper):
    _prop: ElementProperty

    @property
    def unique_id(self):
        return self._prop['uniqueId']

    @property
    def muted(self):
        return self._prop['muted']

    @property
    def name(self):
        return self._prop['name']

    @property
    def overlay_clips(self):
        return [_OverlayClip(prop) for prop in self._prop['overlayClips']]

    @property
    def film_clips(self):
        return [_FilmClip(prop) for prop in self._prop['filmClips']]

    @property
    def audio_clips(self):
        return [_AudioClip(prop) for prop in self._prop['audioClips']]


class _TrackGroup(ITypeWrapper):
    _prop: ElementProperty

    @property
    def tracks(self):
        return [_Track(prop) for prop in self._prop['tracks']]

    @property
    def unique_id(self):
        return self._prop['uniqueId']

    @property
    def muted(self):
        return self._prop['muted']

    @property
    def visible(self):
        return self._prop['visible']

    @property
    def name(self):
        return self._prop['name']


class _Clip(ITypeWrapper):
    _prop: ElementProperty

    @property
    def scene(self):
        return _Scene(self._prop['scene'])

    @property
    def time_frame(self):
        return _TimeFrame(self._prop['timeFrame'])

    @property
    def track_groups(self):
        return [_TrackGroup(prop) for prop in self._prop['trackGroups']]

    @property
    def bookmark_sets(self):
        return self._prop['bookmarkSets']  # [self._BookmarkSet(prop) for prop in self._prop['bookmarkSets']]

    @property
    def fade_in(self):
        return self._prop['fadeIn']

    @property
    def fade_out(self):
        return self._prop['fadeOut']

    @property
    def camera(self):
        return self._prop['camera']

    @property
    def name(self):
        return self._prop['name']

    @property
    def map_name(self):
        return self._prop['mapName']

    @property
    def unique_id(self):
        return self._prop['uniqueId']

    @property
    def active_bookmark_set(self):
        return self._prop['activeBookmarkSet']


class _Session(ITypeWrapper):
    _prop: ElementProperty

    @property
    def unique_id(self):
        return self._prop['uniqueId']

    @property
    def active_clip(self):
        return self._prop['activeClip']

    @property
    def name(self):
        return self._prop['name']

    @property
    def settings(self):
        return _SessionSettings(self._prop['settings'])

    @property
    def clips(self):
        return [_Clip(prop) for prop in self._prop['clips']]


class PragmaFilmMakerProject(ITypeRootWrapper):
    ASSET_TYPE = 'PFMP'
    ASSET_VERSION_MIN = 1
    ASSET_VERSION_MAX = 1
    _root: ElementProperty

    @property
    def session(self):
        return _Session(self._root['session'])
