import logging
import time
import warnings
from pathlib import Path

from dpdispatcher import Machine
from dpdispatcher.dlog import dlog

from thkit import THKIT_ROOT
from thkit.config import loadconfig, validate_config
from thkit.pkg import create_logger


#####ANCHOR Change logfile path
def change_logpath_dispatcher(newlogfile: str):
    """Change the logfile of dpdispatcher."""
    try:
        for hl in dlog.handlers[:]:  # Remove all old handlers
            hl.close()
            dlog.removeHandler(hl)

        fh = logging.FileHandler(newlogfile)
        # fmt = logging.Formatter(
        #     "%(asctime)s | %(name)s-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        # )
        fmt = logging.Formatter(
            "%(asctime)s | dispatch-%(levelname)s: %(message)s", "%Y%b%d %H:%M:%S"
        )
        fh.setFormatter(fmt)
        dlog.addHandler(fh)
        ### Remove the old log file if it exists
        if Path("./dpdispatcher.log").is_file():
            Path("./dpdispatcher.log").unlink()
    except Exception as e:
        warnings.warn(f"Error during change logfile_path {e}. Use the original path.")
    return


def init_jobman_logger(logfile: str | None = None):
    """Initialize the default logger under `log/`, if not provided"""
    if not logfile:
        time_str = time.strftime("%y%m%d_%H%M%S")  # "%y%b%d" "%Y%m%d"
        logfile = f"log/{time_str}_jobman.log"

    logger = create_logger("jobman", level="INFO", log_file=logfile)
    change_logpath_dispatcher(logfile)
    return logger


#####ANCHOR helper functions


def remote_info(machine_dict) -> str:
    """Return the remote machine information.
    Args:
        mdict (dict): the machine dictionary
    """
    remote_path = machine_dict["remote_root"]
    hostname = machine_dict["remote_profile"]["hostname"]
    info_text = f"{' ' * 12}Remote host: {hostname}\n"
    info_text += f"{' ' * 12}Remote path: {remote_path}"
    return info_text


def validate_machine_config(machine_file: str):
    """Validate the YAML file contains multiple machines configs. This function is used to validate machine configs at very beginning of program to avoid later errors.

    Notes:
        - To specify multiple remote machines for the same purpose, the top-level keys in the machine config file should start with the same prefix. Example:
            - `train_1`, `train_2`,... for training jobs
            - `lammps_1`, `lammps_2`,... for lammps jobs
            - `gpaw_1`, `gpaw_2`,... for gpaw jobs
    """
    SCHEMA_MACHINE_FILE = f"{THKIT_ROOT}/jobman/schema/schema_machine.yml"
    schema = loadconfig(SCHEMA_MACHINE_FILE)
    multi_mdict = loadconfig(machine_file)
    for k, mdict in multi_mdict.items():
        validate_config(config_dict={"mydict": mdict}, schema_dict={"mydict": schema["tha"]})

    ### validate each type of machine config
    # for k, v in config.items():
    #     if k.startswith("md"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["tha"]})
    #     elif k.startswith("train"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["train"]})
    #     elif k.startswith("dft"):
    #         validate_config(config_dict={k: v}, schema_dict={k: schema["dft"]})
    return


def check_remote_connection(machine_file: str):
    """Validate the remote connection for multiple machines in the machine config file."""

    def _check_one_machine(machine_dict: dict) -> dict | None:
        ### Revise temporary fields for connection test
        machine_dict["local_root"] = "./"  # tmp local root for connection test
        if machine_dict["context_type"] == "SSHContext":
            machine_dict["remote_profile"]["execute_command"] = (
                f"mkdir -p {machine_dict['remote_root']}"
            )

        try:
            _ = Machine.load_from_dict(machine_dict)
        except Exception as e:
            return {"hostname": machine_dict["remote_profile"]["hostname"], "error": str(e)}
        return None

    multi_mdict = loadconfig(machine_file)
    err_machines = [
        _check_one_machine(mdict["machine"])
        for k, mdict in multi_mdict.items()
        if _check_one_machine(mdict["machine"]) is not None
    ]
    if len(err_machines) > 0:
        raise RuntimeError(f"Cannot connect to remote machines: {err_machines}")
    return


def _parse_multi_mdict(multi_mdict: dict, mdict_prefix: str = "") -> list[dict]:
    """Parse multiple machine dicts from a multi-machine dict based on the prefix.

    Args:
        multi_mdict (dict): the big dict contains multiple machines configs
        mdict_prefix (str): the prefix to select remote machines for the same purpose. Example: 'dft', 'md', 'train'.

    Returns:
        list[dict]: list of machine dicts
    """
    mdict_list = [v for k, v in multi_mdict.items() if k.startswith(mdict_prefix)]
    assert len(mdict_list) > 0, f"No remote machines found for the mdict_prefix: '{mdict_prefix}'"
    return mdict_list


def loadconfig_multi_machines(machine_file: str, mdict_prefix: str = "") -> list[dict]:
    """Load and validate the YAML file contains multiple machine configs. This function to load machine configs for general purpose usage.

    Args:
        machine_file (str): the path of the machine config file

    Returns:
        dict: the multi-machine dict
    """
    validate_machine_config(machine_file)
    multi_mdict = loadconfig(machine_file)
    mdict_list = _parse_multi_mdict(multi_mdict, mdict_prefix)
    return mdict_list
