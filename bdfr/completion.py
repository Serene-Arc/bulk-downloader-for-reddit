#!/usr/bin/env python3

import subprocess
from os import environ
from pathlib import Path

import appdirs


class Completion:
    def __init__(self, shell: str) -> None:
        self.shell = shell
        self.env = environ.copy()
        self.share_dir = appdirs.user_data_dir()
        self.entry_points = ["bdfr", "bdfr-archive", "bdfr-clone", "bdfr-download"]

    def install(self) -> None:
        if self.shell in ("all", "bash"):
            comp_dir = self.share_dir + "/bash-completion/completions/"
            if not Path(comp_dir).exists():
                print("Creating Bash completion directory.")
                Path(comp_dir).mkdir(parents=True, exist_ok=True)
            for point in self.entry_points:
                self.env[f"_{point.upper().replace('-', '_')}_COMPLETE"] = "bash_source"
                with Path(comp_dir + point).open(mode="w") as file:
                    file.write(
                        subprocess.run([point], env=self.env, capture_output=True, text=True).stdout,  # noqa: S603
                    )
                    print(f"Bash completion for {point} written to {comp_dir}{point}")
        if self.shell in ("all", "fish"):
            comp_dir = self.share_dir + "/fish/vendor_completions.d/"
            if not Path(comp_dir).exists():
                print("Creating Fish completion directory.")
                Path(comp_dir).mkdir(parents=True, exist_ok=True)
            for point in self.entry_points:
                self.env[f"_{point.upper().replace('-', '_')}_COMPLETE"] = "fish_source"
                with Path(comp_dir + point + ".fish").open(mode="w") as file:
                    file.write(
                        subprocess.run([point], env=self.env, capture_output=True, text=True).stdout,  # noqa: S603
                    )
                    print(f"Fish completion for {point} written to {comp_dir}{point}.fish")
        if self.shell in ("all", "zsh"):
            comp_dir = self.share_dir + "/zsh/site-functions/"
            if not Path(comp_dir).exists():
                print("Creating Zsh completion directory.")
                Path(comp_dir).mkdir(parents=True, exist_ok=True)
            for point in self.entry_points:
                self.env[f"_{point.upper().replace('-', '_')}_COMPLETE"] = "zsh_source"
                with Path(comp_dir + "_" + point).open(mode="w") as file:
                    file.write(
                        subprocess.run([point], env=self.env, capture_output=True, text=True).stdout,  # noqa: S603
                    )
                    print(f"Zsh completion for {point} written to {comp_dir}_{point}")

    def uninstall(self) -> None:
        if self.shell in ("all", "bash"):
            comp_dir = self.share_dir + "/bash-completion/completions/"
            for point in self.entry_points:
                if Path(comp_dir + point).exists():
                    Path(comp_dir + point).unlink()
                    print(f"Bash completion for {point} removed from {comp_dir}{point}")
        if self.shell in ("all", "fish"):
            comp_dir = self.share_dir + "/fish/vendor_completions.d/"
            for point in self.entry_points:
                if Path(comp_dir + point + ".fish").exists():
                    Path(comp_dir + point + ".fish").unlink()
                    print(f"Fish completion for {point} removed from {comp_dir}{point}.fish")
        if self.shell in ("all", "zsh"):
            comp_dir = self.share_dir + "/zsh/site-functions/"
            for point in self.entry_points:
                if Path(comp_dir + "_" + point).exists():
                    Path(comp_dir + "_" + point).unlink()
                    print(f"Zsh completion for {point} removed from {comp_dir}_{point}")
