from urllib import request, error
import json


def query_appsync(graphql_api_url, graphql_api_key, query):
    data = json.dumps({"query": query})
    r = request.Request(
        headers={"x-api-key": graphql_api_key},
        url=graphql_api_url,
        method="POST",
        data=data.encode("utf8")
    )
    try:
        response = request.urlopen(r).read()
        return json.loads(response.decode("utf8"))
    except error.URLError as ue:
        print("error:", ue)
        return {}


# Must add "accesss" to maintain metadata schema for getItem and add it here
def build_manifest_query(id):
    query = '''query MyQuery {
        getItem(id: "''' + id + '''", websiteId: "Marble"){
            collections {
                display
            }
            contributors {
                display
            }
            copyrightStatement
            copyrightStatus
            createdDate
            creators {
                display
            }
            dedication
            defaultFilePath
            defaultFile {
                id
                mediaResourceId
                mediaServer
            }
            description
            dimensions
            format
            id
            languages {
                display
            }
            level
            linkToSource
            parentId
            parent {
                level
            }
            publishers {
                display
            }
            repository
            sourceSystem
            subjects {
                display
            }
            title
            uniqueIdentifier
            workType
            children {
                items {
                    id
                    level
                    title
                    description
                }
            }
            files {
                items {
                    id
                    mediaResourceId
                    mediaServer
                    mimeType
                }
            }
            }
    }
    '''
    return query


def build_file_query(id):
    query = '''query MyQuery {
        getFile(id: "''' + id + '''"){
            id
            mediaResourceId
            mediaServer
        }
    }
    '''
    return query
