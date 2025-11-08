# Monkey patches for setting user-agent header.

```python
# Importing hooks automatically handles monkey patching
from setuseragent import hooks
# We can set to a specific value
hooks.set_user_agent("my-new-user-agent")
# Or we can set it with a package version
hooks.set_distribution('my-package')
# or using meta package name
hooks.set_distribution(__package__)
```

If using Django, can optionally set the site name as part of the package

```python
from setuseragent.django import set_distribution
set_distribution(__package__)
```
