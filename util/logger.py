#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
def setup_logger():
    '''Prints logger info to terminal'''
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger