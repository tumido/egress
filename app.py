"""S2i app task launcher."""

if __name__ == "__main__":
    from egress import run_task, init_logging
    init_logging()

    run_task()
