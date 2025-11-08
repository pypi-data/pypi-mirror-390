from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site

from setuseragent import agent
from setuseragent import hooks


def set_distribution(name) -> str:
    user_agent = agent.user_agent(name)

    if apps.is_installed("django.contrib.sites"):
        domain = get_current_site(None).domain
        return hooks.set_user_agent(f"{user_agent} (+{domain})")
    else:
        return hooks.set_user_agent(user_agent)
