import logging


def get_logger(name, log_level=logging.INFO, log_format:str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    logging.basicConfig(level=log_level, format=log_format)
    return logging.getLogger(name)



