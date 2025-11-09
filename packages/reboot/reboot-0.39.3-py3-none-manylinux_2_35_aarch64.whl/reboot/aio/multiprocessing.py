import multiprocessing
import sys
import threading
from multiprocessing import forkserver
from rebootdev.aio.once import Once


def _initialize_multiprocessing_start_method():
    multiprocessing_start_method = multiprocessing.get_start_method(
        allow_none=True
    )

    if multiprocessing_start_method is None:
        # We want to use 'forkserver', which should be set before any
        # threads are created, so that users _can_ use threads in
        # their tests and we will be able to reliably fork without
        # worrying about any gotchas due to forking a multi-threaded
        # process.
        multiprocessing.set_start_method('forkserver')
    elif multiprocessing_start_method != 'forkserver':
        raise RuntimeError(
            f"Reboot requires the 'forkserver' start method but you "
            f"appear to have configured '{multiprocessing_start_method}'"
        )

    # When running a Reboot application using something like `pytest`
    # where `__main__` is not the application developers code we might
    # not end up having the module that created the `Application` get
    # preloaded, i.e., imported and executed, on the forkserver,
    # meaning that the child processes will be missing those things
    # too which can lead to unexpected behavior. To try and keep the
    # forkserver, and thus the children processes, as identical to the
    # parent process at the point we constructed the `Application` we
    # preload all of the modules that have already been loaded.
    #
    # NOTE: for applications that require this behavior we've also
    # noticed that at least Python version 3.10 does not appear to
    # correctly work, but 3.12.11 has been tested successfully. At
    # some point we may want to revisit how we do this but for now
    # this is a stop gap measure to enable things like `pytest`.
    multiprocessing.set_forkserver_preload(list(sys.modules.keys()))

    # We've encountered issues when the forkserver was started while threads
    # were already running, especially if those threads were calling Objective-C
    # code, which is not allowed on macOS.
    # To avoid this, we force the forkserver to start as early as possible,
    # ensuring it runs before any other code creates threads.
    # If threads are already running when we attempt to start the forkserver,
    # and it fails, we will raise a clear error.
    try:
        forkserver.ensure_running()
    except BaseException as e:
        if threading.active_count() > 1:
            raise RuntimeError(
                f"Forkserver failed to start. {threading.active_count()} "
                "threads were already running before the attempt, "
                "which may have caused to the issue. Ensure no threads are "
                "created before initializing Reboot. Active threads:\n"
                "\n".join([thread.name for thread in threading.enumerate()])
            ) from e
        else:
            raise


# We're using a global here because we only want to initialize the
# multiprocessing start method once per process.
initialize_multiprocessing_start_method_once = Once(
    _initialize_multiprocessing_start_method
)
