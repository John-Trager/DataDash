from lib.utils import RollingVarianceCalculator, Timer, SMAVariance
import random

if __name__ == "__main__":

    # make list of x random floats
    length = 100_000
    data = [random.uniform(0, 1.5) for _ in range(length)]

    win_sizes = [10, 50, 100, 500, 1000]

    print("RollingVarianceCalculator (old implementation)")

    for win_size in win_sizes:
        rvc = RollingVarianceCalculator(win_size)

        timer = Timer()

        for d in data:
            rvc.update(d)

        elapsed = timer.elapsed()

        print(
            f"Time to calculate rolling variance for {length} data points and win size {win_size}: {elapsed} seconds, avg update time: {elapsed/length} seconds (hz: {1/(elapsed/length)})"
        )

    print("--- --- ---")
    print("SMAVariance (new implementation")
    for win_size in win_sizes:
        sma = SMAVariance(win_size)

        timer = Timer()

        for d in data:
            sma.update(d)

        elapsed = timer.elapsed()

        print(
            f"Time to calculate sma variance for {length} data points and win size {win_size}: {elapsed} seconds, avg update time: {elapsed/length} seconds (hz: {1/(elapsed/length)})"
        )
