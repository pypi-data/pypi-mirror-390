import time


def high_precision_sleep(duration_sec: float):
    # init
    start_time = time.perf_counter()
    target_time = start_time + duration_sec

    # --- passive wait phase ---
    while True:
        remaining_time = target_time - time.perf_counter()
        if remaining_time > 0.01:
            time.sleep(0.5 * remaining_time)
        else:
            break

    # --- active wait phase ---
    estimated_cycle_time = 0.0  # estimated time of 1 active wait cycle
    active_wait_start_time = time.perf_counter()
    iters = 0
    while True:
        # check if we need to stop
        if time.perf_counter() > (target_time - 0.5 * estimated_cycle_time):
            # stopping now is closer to the target time than doing another cycle
            break

        # update estimated cycle time
        iters += 1
        estimated_cycle_time = (time.perf_counter() - active_wait_start_time) / iters
