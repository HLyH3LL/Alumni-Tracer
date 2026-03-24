from .models1 import SiteConfig


def site_config(request):
    """
    Make `config` available to templates consistently (footer, colors, etc.).
    """
    try:
        config = SiteConfig.get_config()
    except Exception:
        config = None
    return {"config": config}

