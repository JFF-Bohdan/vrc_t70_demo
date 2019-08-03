from loguru import logger


def main():
    logger.info("daemon started")
    logger.info("daemon finished")
    return 0


if __name__ == "__main__":
    res = main()
    exit(res)
