import os
import subprocess as sp
from concurrent.futures import ProcessPoolExecutor, wait, Future, CancelledError
from pathlib import Path
from sys import stdin
from typing import Generator, Iterable
import signal

import torch


def wait_and_handle_interrupt(jobs: list[tuple[Future, str]], pool: ProcessPoolExecutor):
    """Handle KeyboardInterrupt gracefully when waiting for jobs to complete."""
    flag_interrupt, interrupt_urgency = False, 0
    num_finished, num_canceled = 0, 0

    def handle_keyboard_interrupt(signum, frame):
        nonlocal flag_interrupt, interrupt_urgency
        flag_interrupt = True
        interrupt_urgency += 1

    old_handler = signal.signal(signal.SIGINT, handle_keyboard_interrupt)

    try:
        while jobs:
            # Poll for completed jobs with a timeout to check for interrupts
            try:
                done, not_done = wait([fut for fut, _ in jobs], return_when="FIRST_COMPLETED", timeout=0.5)

                # Print info about completed or cancelled jobs since the last poll
                for fut in done:
                    cmd = next(cmd for fut2, cmd in jobs if fut2 == fut)
                    try:
                        result = fut.result()
                        print(f"Job '{cmd}' completed with return code {result.returncode}")
                        num_finished += 1
                    except CancelledError:
                        print(f"Job with args '{cmd}' was cancelled")
                        num_canceled += 1
            except KeyboardInterrupt:
                # If wait() is interrupted, we actually handle it in the handle_keyboard_interrupt 
                # function. Pass here, and *actually* handle it in the 'interrupt_urgency' logic.
                pass

            # Update the set of jobs to only include those not done (where 'done' means finished
            # or cancelled)
            jobs = [(fut, cmd) for fut, cmd in jobs if fut not in done]

            # If an interrupt was received during the wait, handle it
            if flag_interrupt:
                flag_interrupt = False  # Debounce multiple signals
                if interrupt_urgency == 1:
                    print("Canceling pending subprocesses but leaving running ones alone.")
                    running = []
                    for fut, cmd in jobs:
                        if fut.running():
                            running.append(cmd)
                        else:
                            fut.cancel()
                    print("The following jobs are still running:")
                    for cmd in running:
                        print(f"  {cmd}")
                    print("Press Ctrl-C again to forcefully terminate everything.")
                elif interrupt_urgency == 2:
                    print("Forcefully shutting down.")
                    pool.shutdown(wait=False, cancel_futures=True)
                    return
    finally:
        signal.signal(signal.SIGINT, old_handler)

def run_pool_round_robin_devices(commands: Iterable[str], device_ids: list[int]):
    print("Creating pool with", len(device_ids), "workers")
    pool = ProcessPoolExecutor(max_workers=len(device_ids))
    jobs = []
    for i, cmd in enumerate(commands):
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = f"cuda:{device_ids[i % len(device_ids)]}"
        future = pool.submit(sp.run, cmd, shell=True, check=True, env=env)
        jobs.append((future, cmd))
    wait_and_handle_interrupt(jobs, pool)


def iter_stdin_lines() -> Generator[str, None, None]:
    for line in stdin:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gpus", type=int, nargs="+", default=[0])
    parser.add_argument("--jobs-file", type=Path, default=None)
    args = parser.parse_args()

    # Check that all devices exist
    for d in args.gpus:
        # This will raise an error if the device doesn't exist
        torch.cuda.get_device_properties(d)

    if args.jobs_file is not None:
        with open(args.jobs_file, "r") as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        run_pool_round_robin_devices(commands, args.gpus)
    else:
        # Accept piped-in commands from stdin
        run_pool_round_robin_devices(iter_stdin_lines(), args.gpus)
