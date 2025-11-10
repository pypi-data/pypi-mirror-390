from random import shuffle, uniform
from time import sleep

num = int | float


def stalinsort(lst: list[num]) -> list[num]:
    """Sends Non-Confirming numbers to the gulag! First number always gets a pass."""

    sort = [lst[0]]
    for n in lst:
        if n > sort[-1]:
            sort.append(n)

    lst = sort
    return lst


def bogosort(lst: list[num]) -> list[num]:
    """Randomly shuffles all items until sorted"""

    while lst != sorted(lst):
        shuffle(lst)

    return lst


def intelligentdesignsort(lst: list[num]) -> list[num]:
    """An intelligent designer must have made this list. Thus, we shouldn't meddle with it."""

    return lst


def miraclesort(lst: list[num]) -> list[num]:
    """Wait for a miracle to happen"""

    while lst != sorted(lst):
        sleep(1)

    return lst


def movinggoalpostsort(lst: list[num]) -> str:
    """Redefines mathematics."""

    msg = "<".join(map(str, lst))
    msg += ", so the list is already sorted."
    return msg


def internsort(lst: list[num]) -> list[num]:
    """Let the intern do it for you!"""

    print("Creating a jira ticket...")
    sleep(10)
    print("The intern quit.")
    return lst


def orwellsort(lst: list[num]) -> list[num]:
    """Oceania allows no individuality."""

    lst = [1 for _ in lst]
    return lst


def monkeysort(lst: list[num], printOutput: bool = False) -> list[num]:
    """Shakespeares Monkeys can do the work"""

    while lst != sorted(lst):
        lst = [uniform(float(sorted(lst)[0]), float(sorted(lst)[-1])) for _ in lst]

        if printOutput:
            print(lst)

    return lst


def zerosort(lst: list[num]) -> list[num]:
    """The list is sorted if all numbers are multiplied by 0!"""

    lst = [int(n * 0) for n in lst]
    return lst


def smallchildsort(lst: list[num], giveCandy: bool = False) -> str:
    """Why are you giving the list to a small child????"""

    lst = sorted(lst)
    if not giveCandy:
        return "I have the list, but I wont give it! Hmph!"

    del lst
    return ":000 CANDY!!!!!!!! *runs away, but drops the list, breaking it*"


if __name__ == "__main__":
    print(smallchildsort([1, 5, 7, 3, 2, 91.92]))
