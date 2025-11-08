from django.apps import AppConfig
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from setuseragent import agent, hooks

DEFAULT_DISTRIBUTION = getattr(settings, "USER_AGENT_DISTRIBUTION", __package__)


class CustomConfig(AppConfig):
    name = "setuseragent.django"

    def ready(self):
        user_agent = agent.user_agent(DEFAULT_DISTRIBUTION)

        if self.apps.is_installed("django.contrib.sites"):
            domain = get_current_site(None).domain
            return hooks.set_user_agent(f"{user_agent} (+{domain})")
        else:
            return hooks.set_user_agent(user_agent)
