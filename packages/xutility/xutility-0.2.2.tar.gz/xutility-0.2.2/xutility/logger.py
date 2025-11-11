import pathlib
import sys
from typing import Literal

from loguru import logger

DEFAULT_LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSSSSS}</green> | <level>{level: <8}</level> | <level>{message}</level> (<cyan>{name}</cyan>:<cyan>{line}</cyan>)"


def setup_logger(
    service_name: str,
    module_name: str = "",
    file_level: Literal["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
    echo_level: Literal["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    log_base_dir: pathlib.Path = pathlib.Path.home() / "logs",
    log_fmt: str = DEFAULT_LOG_FORMAT,
) -> None:
    """Log to `log_base_dir/service_name/service_name.YYYY-MM-DD.log or module_name.YYYY-MM-DD.log` with daily rotation

    Args:
        service_name (str): _description_
        module_name (str, optional): _description_. Defaults to "".
        file_level (Literal[&quot;&quot;, &quot;DEBUG&quot;, &quot;INFO&quot;, &quot;WARNING&quot;, &quot;ERROR&quot;, &quot;CRITICAL&quot;], optional): _description_. Defaults to "DEBUG".
        echo_level (Literal[&quot;&quot;, &quot;DEBUG&quot;, &quot;INFO&quot;, &quot;WARNING&quot;, &quot;ERROR&quot;, &quot;CRITICAL&quot;], optional): _description_. Defaults to "".
        log_base_dir (pathlib.Path, optional): _description_. Defaults to pathlib.Path.home()/"logs".
        log_fmt (str, optional): _description_. Defaults to DEFAULT_LOG_FORMAT.
    """
    logger.configure(handlers=None)
    all_handlers_cfg: list = []
    # echo handler to stdout/stderr
    if echo_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        echo_handler_cfg = dict(sink=sys.stdout, level=echo_level, format=log_fmt)
        all_handlers_cfg.append(echo_handler_cfg)
    # file handler
    if file_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        if not module_name:
            sink_path = log_base_dir / service_name / (service_name + ".{time:YYYY-MM-DD}" + ".log")
        else:
            sink_path = log_base_dir / service_name / (module_name + ".{time:YYYY-MM-DD}" + ".log")
        file_handler_cfg = dict(sink=sink_path, level=file_level, rotation="00:00", format=log_fmt)
        all_handlers_cfg.append(file_handler_cfg)
    logger.configure(handlers=all_handlers_cfg)
