def return_provider(repository: str, level: str) -> dict:
    if not repository or not level or level == 'file':
        return
    repository = repository.lower()
    if (repository == 'museum'):
        return _snite_proivider()
    elif (repository == 'unda'):
        return _archives_proivider()
    elif (repository == 'rare' or repository == 'curate' or repository == 'archt'):
        return _rbsc_proivider()
    elif (repository == 'hesb'):
        return _hesb_proivider()
    else:
        raise Exception("bad provider " + repository.lower())
        return


def _snite_proivider() -> dict:
    return {
        "id": "https://sniteartmuseum.nd.edu/about-us/contact-us/",
        "type": "Agent",
        "label": {"en": ["Snite Museum of Art"]},
        "homepage": [
            {
                "id": "https://sniteartmuseum.nd.edu",
                "type": "Text",
                "label": {"en": ["Snite Museum of Art"]},
                "format": "text/html"
            }
        ],
        "logo": [
            {
                "id": "https://sniteartmuseum.nd.edu/stylesheets/images/snite_logo@2x.png",
                "type": "Image",
                "format": "image/png",
                "height": 100,
                "width": 120
            }
        ]
    }


def _rbsc_proivider() -> dict:
    return {
        "id": "https://rarebooks.library.nd.edu/using",
        "type": "Agent",
        "label": {"en": ["Rare Books and Special Collections, Hesburgh Libraries, University of Notre Dame"]},
        "homepage": [
            {
                "id": "https://rarebooks.library.nd.edu/",
                "type": "Text",
                "label": {"en": ["Rare Books and Special Collections, Hesburgh Libraries, University of Notre Dame"]},
                "format": "text/html"
            }
        ],
        "logo": [
            {
                "id": "https://rarebooks.library.nd.edu/images/hesburgh_mark.png",
                "type": "Image",
                "format": "image/png",
                "height": 100,
                "width": 120
            }
        ]
    }


def _archives_proivider() -> dict:
    return {
        "id": "http://archives.nd.edu/about/",
        "type": "Agent",
        "label": {"en": ["University of Notre Dame Archives, Hesburgh Libraries, University of Notre Dame"]},
        "homepage": [
            {
                "id": "http://archives.nd.edu/",
                "type": "Text",
                "label": {"en": ["University of Notre Dame Archives"]},
                "format": "text/html"
            }
        ],
        "logo": [
            {
                "id": "https://rarebooks.library.nd.edu/images/hesburgh_mark.png",
                "type": "Image",
                "format": "image/png",
                "height": 100,
                "width": 120
            }
        ]
    }


def _hesb_proivider() -> dict:
    return {
        "id": "https://library.nd.edu",
        "type": "Agent",
        "label": {"en": ["General Collection, Hesburgh Libraries"]},
        "homepage": [
            {
                "id": "https://library.nd.edu/",
                "type": "Text",
                "label": {"en": ["General Collection, Hesburgh Libraries"]},
                "format": "text/html"
            }
        ],
        "logo": [
            {
                "id": "https://library.nd.edu/static/media/library.logo.43a05388.png",
                "type": "Image",
                "format": "image/png",
                "height": 100,
                "width": 120
            }
        ]
    }
