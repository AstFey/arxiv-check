import ssl


def build_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    if context.get_ca_certs():
        return context

    cert_path = _find_cert_bundle()
    if cert_path:
        context.load_verify_locations(cafile=cert_path)
    return context


def _find_cert_bundle():
    try:
        import certifi  # type: ignore

        return certifi.where()
    except ImportError:
        pass

    try:
        from pip._vendor.certifi import where as certifi_where  # type: ignore

        return certifi_where()
    except ImportError:
        return None

