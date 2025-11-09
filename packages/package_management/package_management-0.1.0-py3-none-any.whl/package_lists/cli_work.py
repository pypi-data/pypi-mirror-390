from src.type.packages import PackageManager, CLIPackage


class Htop(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.APT : "htop"
    }

class Bat(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.APT : "bat"
    }

# Fuzzy find in terminal, https://github.com/junegunn/fzf
class Fzf(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.APT : "fzf"
    }

# Better ls, https://github.com/eza-community/eza
class Eza(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.BREW : "eza"
    }

# Better du, https://github.com/bootandy/dust
class DuDust(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.BREW : "dust"
    }

# Better df, https://github.com/muesli/duf
class Duf(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.APT : "duf"
    }

# Better find, https://github.com/sharkdp/fd
class FdFind(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.APT : "fd-find"
    }

# Better grep, https://github.com/BurntSushi/ripgrep
class Ripgrep(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.BREW : "ripgrep"
    }

# Better man pages, https://github.com/tldr-pages/tldr
class Tldr(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.BREW : "tlrc"
    }

class Yq(CLIPackage):
    package_dict: dict[PackageManager, str] = {
        PackageManager.SNAP : "yq"
    }


#!----- Interesting ---------!#
# Easier curl for APIs, # https://github.com/httpie/cli
# https://github.com/Aider-AI/aider
# AWS Stack Mock locally https://github.com/localstack/localstack
# Docker container for any distro, https://github.com/89luca89/distrobox
# Ubuntu VM easy, https://github.com/canonical/multipass
# AI auto tab assistant, https://github.com/TabbyML/tabby
# Create CLI's, https://github.com/spf13/cobra
# Better git diff, https://github.com/dandavison/delta

