from abc import ABCMeta

from .custom_excepthook import transmit_exception


class ExceptionMeta(ABCMeta):
    """
    Metaclass to add `capture_even_if_caught` functionality to exceptions
    and provide a `transmit_to_sailfish` method for all exceptions.
    """

    def __new__(cls, name, bases, dct):
        # Wrap or define the `__init__` method
        if "__init__" in dct:
            original_init = dct["__init__"]

            def wrapped_init(self, *args, **kwargs):
                # Add the `capture_even_if_caught` attribute
                self.capture_even_if_caught = kwargs.pop(
                    "capture_even_if_caught", False
                )
                self._handled = False  # Ensure `_handled` is initialized
                original_init(self, *args, **kwargs)

            dct["__init__"] = wrapped_init
        else:

            def default_init(self, *args, **kwargs):
                # Add the `capture_even_if_caught` attribute
                self.capture_even_if_caught = kwargs.pop(
                    "capture_even_if_caught", False
                )
                self._handled = False  # Ensure `_handled` is initialized
                super(Exception, self).__init__(*args, **kwargs)

            dct["__init__"] = default_init

        # Add `transmit_to_sailfish` method to all exceptions
        def transmit_to_sailfish(self, was_caught: bool = False):
            """
            Transmit this exception to Sailfish.
            """
            if not getattr(self, "_handled", False):
                transmit_exception(type(self), self, self.__traceback__, was_caught)
                setattr(
                    self, "_handled", True
                )  # Mark as handled to prevent duplication

        dct["transmit_to_sailfish"] = transmit_to_sailfish

        return super().__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        """
        Intercept exception instantiation to handle `capture_even_if_caught`.
        """
        instance = super().__call__(*args, **kwargs)
        # Automatically handle `capture_even_if_caught` exceptions
        if getattr(instance, "capture_even_if_caught", False):
            instance.transmit_to_sailfish()
        return instance


class PatchedException(Exception, metaclass=ExceptionMeta):
    """
    A patched version of the built-in Exception class with universal interception capabilities.
    """

    pass
