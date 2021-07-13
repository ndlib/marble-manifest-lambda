# public_graphql_lambda
This lambda will be called by an API Gateway.
It will look up the AppSync API Keys from SSM, attach that key to the header, and make a call to AppSync.  The results of that query will be returned to the calling process.

# Requirements
Required parameters include:
    event['resource'] = '/query/{id}'
    event['pathParameters'] = {"id": "listPublicFeaturedPortfolioCollections"}
    event['body'] = '''query MyQuery {
        listPublicFeaturedPortfolioCollections {
            items {
                portfolioUserId
                portfolioCollectionId
                description
                featuredCollection
                highlightedCollection
                layout
                imageUri
                privacy
            }
        }
    }'''


If the query in the body does not start with "query", then we concatenate "query MyQuery {" + {the query that is passed} + "}"

The expected API signature must be one of these:
* /query/listPublicPortfolioCollections
* /query/listHighlightedPortfolioCollections
* /query/listPublicFeaturedPortfolioCollections
* /query/getExposedPortfolioCollection
