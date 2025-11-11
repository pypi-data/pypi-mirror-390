def get_default_headers(ttl, version, timestamp):
    return {
        'last_updated': timestamp,
        'ttl': ttl,
        'version': version,
        'data': {}
    }
