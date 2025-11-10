from src.type.packages import PackageManager, GUIPackage


class VSCodium(GUIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.NIX : "nixpkgs.vscodium"
    }

# class Lens(Package):
#     package_dict: dict[PackageManager, str] = {
#         PackageManager.NIX : "nixpkgs.lens"
#     }

class Gitkraken(GUIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.FLATPAK : "com.axosoft.GitKraken"
    }

class IntelliJ(GUIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.FLATPAK : "com.jetbrains.IntelliJ-IDEA-Community"
    }


#!----- Interesting ---------!#
# Remote IDE tool, https://github.com/loft-sh/devpod
# Wordpress for backend admin panels, https://github.com/appsmithorg/appsmith?tab=readme-ov-file
# React framework close to no-code, https://github.com/refinedev/refine
# API Interactive GUI, https://github.com/hoppscotch/hoppscotch

