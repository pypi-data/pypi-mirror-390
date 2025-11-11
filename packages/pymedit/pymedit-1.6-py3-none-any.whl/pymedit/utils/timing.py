import time

# tic and toc for easy timing
tclock = dict()


def tic(ref: str | int = 0):
    """
    Starts timer, stop timer with with `toc(ref)`

    Current time is stored in tclock[ref]
    """
    global tclock
    tclock[ref] = time.time()


def toc(ref=0,fmt="0.2f"):
    global tclock
    return format(time.time()-tclock[ref], fmt)+"s"

