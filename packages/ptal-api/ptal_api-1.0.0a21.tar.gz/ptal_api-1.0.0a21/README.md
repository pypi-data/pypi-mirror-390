# ptal-api

Python adapter for Talisman-based app

How to create trivial adapter:

    graphql_url = 'https://demo.talisman.ispras.ru/graphql' # or another talisman-based app
    auth_url = 'https://demo.talisman.ispras.ru/auth/'
    realm = 'demo'
    client_id = 'web-ui'
    client_secret = '<some-secret>'

    gql_client = KeycloakAwareGQLClient(
        graphql_url, 10000, 5,
        auth_url=auth_url,
        realm=realm, client_id=client_id, user='admin', pwd='admin',
        client_secret=client_secret
    ).__enter__()

    adapter = TalismanAPIAdapter(gql_client, {})

    c = adapter.get_concept('ОК-123456')
