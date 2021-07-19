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


def media_canvas(iiif_base_url: str, media_json: dict) -> dict:
    media_type = ""
    if is_audio(media_json):
        media_type = 'Sound'
    elif is_video(media_json):
        media_type = "Video"
    if not media_type:
        return {}
    return {
        'id': _canvas_id(iiif_base_url, media_json.get('id', '')),
        'type': 'Canvas',
        'items': [_annotation_page(iiif_base_url, media_json, media_type)]
    }


def _annotation_page(iiif_base_url: str, media_json: dict, media_type: str) -> dict:
    return {
        'id': _annotation_page_id(iiif_base_url, media_json.get('id', '')),
        'type': 'AnnotationPage',
        'items': [_annotation(iiif_base_url, media_json, media_type)]
    }


def _annotation(iiif_base_url: str, media_json: dict, media_type: str) -> dict:
    return {
        'id': _annotation_id(iiif_base_url, media_json.get('id', '')),
        'type': 'Annotation',
        'motivation': 'painting',
        'target': _annotation_page_id(iiif_base_url, media_json.get('id', '')),
        'body': _media(media_json, media_type)
    }


def _media(media_json: dict, media_type: str) -> dict:
    return {
        'id': _media_url_id(media_json),
        'type': media_type,
        'format': media_json.get('mimeType', 'audio/mp4')
    }


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
