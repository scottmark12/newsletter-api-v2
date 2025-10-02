from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source","utm_medium","utm_campaign","utm_term","utm_content",
    "fbclid","gclid","mc_cid","mc_eid","igshid","ref","ref_src","ref_url"
}

def canonicalize_url(url: str) -> str:
    u = urlparse(url)

    # strip fragments
    u = u._replace(fragment="")

    # normalize AMP and trailing slash
    path = u.path.rstrip("/")
    if path.endswith("/amp"):
        path = path[:-4]
    if path.endswith(".amp"):
        path = path[:-4]
    u = u._replace(path=path)

    # drop tracking params, sort remaining for stability
    q = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
         if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")]
    q.sort()
    u = u._replace(query=urlencode(q, doseq=True))

    s = urlunparse(u)
    return s.rstrip("/")


def sha1(s: str) -> str:
    # small helper kept for schema parity
    import hashlib
    return hashlib.sha1(s.encode("utf-8")).hexdigest()
