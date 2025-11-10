from loguru import logger

logger.add(
    "decache.log",
    rotation="50 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
