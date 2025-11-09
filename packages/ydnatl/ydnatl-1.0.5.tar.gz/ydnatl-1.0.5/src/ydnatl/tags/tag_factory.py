from ydnatl.core.element import HTMLElement


# Factory function to create simple tag classes
def simple_tag_class(tag, self_closing=False, extra_init=None):
    class _Tag(HTMLElement):
        def __init__(self, *args, **kwargs):
            if extra_init:
                extra_init(self, kwargs)
            super().__init__(
                *args,
                **{
                    **kwargs,
                    "tag": tag,
                    **({"self_closing": True} if self_closing else {}),
                },
            )

    _Tag.__name__ = tag.capitalize() if tag.islower() else tag
    return _Tag
