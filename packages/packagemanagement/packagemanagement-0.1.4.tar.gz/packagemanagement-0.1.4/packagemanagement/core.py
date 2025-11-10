import subprocess
import inspect

from packagemanagement.config.globals import set_ordered_managers, get_ordered_managers
from typing import IO
from types import ModuleType
from packagemanagement.type.packages import Package, PackageManager, PackageType
from getpass import getpass
from logging import getLogger

logger = getLogger(__name__)

def install_packages(p_list: list[Package], passwd: str, er_log: IO, inf_log: IO):
    ordered_managers = get_ordered_managers()
    for package in p_list:
        pref = package.which_package_manager(ordered_managers=ordered_managers)
        check_command = PackageManager.get_check_command(pref, package)
        result = subprocess.run(check_command, shell=True, capture_output=True)
        if result.stdout != b"":
            logger.info(f"==== {package.get_package_name(pref)} seems to already be installed with manager {pref}. ===")
        elif result.stderr != b"":
            raise RuntimeError(f"Error installing {package.get_package_name(pref)} when using manager {pref}")
        else:
            command = PackageManager.get_install_command(pref, package)
            kwargs = {"args": command, "check": True, "stderr": er_log, "stdout": inf_log}

            sudo_required_pm = {PackageManager.APT, PackageManager.SNAP}
            if package.allow_sudo() and pref in sudo_required_pm:
                kwargs["args"] = "sudo -S " + command
                kwargs["input"] = passwd

            logger.info(subprocess.run(**kwargs, shell=True, text=True))

def list_packages_to_install(mod: ModuleType) -> list[Package]:
    # Iterate through all classes defined in the module
    ps = []
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        # Check if the class is defined in this module (not imported)
        if obj.__module__ == mod.__name__:
            # Check if it’s a subclass of MyBaseClass (but not the base itself)
            if issubclass(obj, Package) and obj is not Package:
                ps.append(obj())
    return ps


def runner(allowed_managers_for_each_type: dict[PackageType, list[PackageManager]], modules_with_packages: list[ModuleType]):
    set_ordered_managers(ordered_managers=allowed_managers_for_each_type)
    password = getpass("Sudo Password: ")

    with open("err.log", "w+") as err_log:
        with open("info.log", "w+") as info_log:
            for m in modules_with_packages:
                packs = list_packages_to_install(m)
                install_packages(packs, er_log=err_log, inf_log=info_log, passwd=password)




