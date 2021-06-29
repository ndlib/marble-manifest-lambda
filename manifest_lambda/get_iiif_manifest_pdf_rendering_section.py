import os


def return_pdf_rendering(standard_json: dict) -> dict:
    first_pdf_json = _return_first_pdf_media_item(standard_json)
    if not first_pdf_json:
        return {}
    else:
        return _pdf_rendering(first_pdf_json)


def _return_first_pdf_media_item(standard_json: dict) -> dict:
    for media_item in standard_json.get('media', {}).get('items', []):
        if '.pdf' in media_item.get('mediaResourceId') or media_item.get('mimeType') == 'application/pdf':
            return media_item
    return {}


def _pdf_rendering(pdf_json: dict) -> dict:
    if not pdf_json.get('mediaResourceId', '') or not pdf_json.get('mediaServer', ''):
        return {}
    mediaResourceId = pdf_json.get('mediaResourceId', '')
    if not mediaResourceId.startswith('media'):
        mediaResourceId = 'media%2F' + mediaResourceId
    return [
        {
            "id": os.path.join(pdf_json.get('mediaServer', ''), mediaResourceId),
            "type": "Text",
            "label": {"en": ["PDF version"]},
            "format": pdf_json.get('mediaType', 'application/pdf')
        }
    ]
