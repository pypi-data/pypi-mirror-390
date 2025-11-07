from btweak.helpers.cmdhandler import run_system_commands
from os.path import exists
import subprocess
import sys
from rich import print


def fix_berserkarch_gpg_pacman():
    fix_db_lck()
    run_system_commands(
        [
            "sudo pacman-key --init",
            "sudo pacman-key --populate",
            "curl -s https://thehackersbrain.xyz/pubkey.asc | gpg --import",
            "gpg --export B024DCEFADEF4328B5E3A848E7E0F2B78484DACF | sudo pacman-key --add -",
            "sudo pacman-key --lsign-key B024DCEFADEF4328B5E3A848E7E0F2B78484DACF",
            "sudo pacman -Syy --noconfirm",
        ]
    )


def fix_db_lck():
    fname = "/var/lib/pacman/db.lck"
    if exists(fname):
        result = subprocess.run(
            ["pgrep", "-x", "pacman"], capture_output=True, text=True
        )
        if result.stdout.strip():
            print("(x) Pacman is currently running! Aborting unlock.")
            sys.exit(1)
        else:
            run_system_commands("sudo rm -rf /var/lib/pacman/db.lck")
    else:
        print("(✓) No lock file found. Pacman DB is clean.")
