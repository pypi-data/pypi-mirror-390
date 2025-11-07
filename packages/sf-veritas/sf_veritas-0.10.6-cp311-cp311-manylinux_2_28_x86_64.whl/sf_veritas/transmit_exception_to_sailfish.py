from .custom_excepthook import transmit_exception


def transmit_exception_to_sailfish(
    exc: BaseException,
    force_transmit: bool = False,
):
    """
    Transmit an exception to Sailfish using the original traceback captured at the
    point the exception was raised.

    :param exc: The exception instance.
    :param force_transmit: If True, will transmit even if the exception might
                           have already been handled or flagged.
    """
    # Get the exception type and traceback from the exception itself
    exc_type = type(exc)
    exc_traceback = exc.__traceback__  # Automatically fetch the original traceback

    # In some implementations, you might keep a `_handled` attribute to avoid double transmission.
    if not force_transmit and getattr(exc, "_handled", False):
        return  # Already transmitted

    # Actually send it over to Sailfish
    transmit_exception(exc_type, exc, exc_traceback)

    # Mark as handled to avoid re-transmission
    setattr(exc, "_handled", True)
