from urllib.parse import urlparse, urlunparse


def mask_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.username and parsed.password:
            # Replace password with ***
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            masked_url = urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))
            return masked_url
        return url
    except Exception as e:
        return "[Invalid URL]"
