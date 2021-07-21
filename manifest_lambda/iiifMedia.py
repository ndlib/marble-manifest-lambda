import os


def is_media(media_json) -> bool:
    if is_audio(media_json) or is_video(media_json):
        return True
    return False


def is_audio(media_json: dict) -> bool:
    if media_json.get('mimeType', '').startswith('audio/') and media_json.get('mediaServer', '') and media_json.get('mediaResourceId', ''):
        return True
    return False


def is_video(media_json: dict) -> bool:
    if media_json.get('mimeType', '').startswith('video/') and media_json.get('mediaServer', '') and media_json.get('mediaResourceId', ''):
        return True
    return False


def media_annotation_page(iiif_base_url: str, media_json: dict, default_duration: float) -> dict:
    return {
        'id': _annotation_page_id(iiif_base_url, media_json.get('id', '')),
        'type': 'AnnotationPage',
        'items': [_annotation(iiif_base_url, media_json, default_duration)]
    }


def _annotation(iiif_base_url: str, media_json: dict, default_duration: float) -> dict:
    return {
        'id': _annotation_id(iiif_base_url, media_json.get('id', '')),
        'type': 'Annotation',
        'motivation': 'painting',
        'target': _annotation_page_id(iiif_base_url, media_json.get('id', '')),
        'body': _media(media_json, default_duration)
    }


def _media(media_json: dict, default_duration: float) -> dict:
    media_type = "Sound"
    if is_audio(media_json):
        media_type = 'Sound'
    elif is_video(media_json):
        media_type = "Video"
    duration = media_json.get('duration', default_duration)
    results = {
        'id': _media_url_id(media_json),
        'type': media_type,
        'format': media_json.get('mimeType', 'audio/mp4')
    }
    if duration:
        results['duration'] = duration
    if media_type == 'Video':
        results['height'] = media_json.get('height', 2000)
        results['width'] = media_json.get('width', 2000)
    return results


def _media_url_id(media_json: dict) -> str:
    return os.path.join(media_json.get('mediaServer', ''), media_json.get('mediaResourceId', ''))


def _annotation_id(iiif_base_url: str, media_id: str):
    return _build_id(iiif_base_url, 'annotation', media_id)


def _annotation_page_id(iiif_base_url: str, media_id: str):
    return _build_id(iiif_base_url, 'annotation_page', media_id)


def _canvas_id(iiif_base_url: str, media_id: str):
    return _build_id(iiif_base_url, 'canvas', media_id)


def _build_id(iiif_base_url: str, id_type: str, media_id: str) -> str:
    return os.path.join(iiif_base_url, id_type, media_id.replace("/", "%2F"))
