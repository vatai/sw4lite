#!/usr/bin/env python
import os
import re
import sys
from subprocess import CompletedProcess
from typing import Optional

from tadashi.apps import App
from tadashi.translators import Translator

ml4tadashi = os.path.dirname(__file__)
ml4tadashi = os.path.dirname(ml4tadashi)
ml4tadashi = os.path.dirname(ml4tadashi)
ml4tadashi = os.path.dirname(ml4tadashi)
sys.path.append(ml4tadashi)
ml4tadashi = os.path.join(ml4tadashi, "ML4TADASHI")
sys.path.append(ml4tadashi)

import ML4TADASHI


class Sw4Lite(App):
    def __init__(
        self,
        source="src/ew-cfromfort.C",
        translator: Optional[Translator] = None,
        compiler_options: list = None,
        ephemeral: bool = False,
        populate_scops: bool = True,
    ):
        super().__init__(
            source=source,
            translator=translator,
            compiler_options=compiler_options,
            ephemeral=ephemeral,
            populate_scops=populate_scops,
        )

    def codegen_init_args(self):
        return {}

    def app_required_options(self) -> list[str]:
        return ["-Isrc/double"]

    def compile_cmd(self, suffix: str) -> list[str]:
        self.source.with_suffix(".c").touch()
        self.source.with_suffix(".o").touch()
        cmd = [
            "make",
            "-j",
            "ckernel=yes",
            f"SOURCE={self.source.with_suffix('').name}",
            f"APP={self.output_binary.name}",
            "CC=mpiclang",
            "CXX=mpiclang++",
        ]
        return cmd

    def run_cmd(self) -> list[str]:
        cmd = [
            f"./optimize_c/{self.output_binary.name}",
            "tests/pointsource/pointsource.in",
        ]
        return cmd

    def extract_runtime(self, proc: CompletedProcess) -> float:
        stdout = proc.stdout.decode()
        print(stdout)
        lines = stdout.split("\n")
        pattern = re.compile(r" Total running time:.*(\d+\.\d+).*")
        for line in lines:
            match = pattern.match(line)
            if match:
                return float(match.groups()[0])
        raise Exception("No output found")


def main():
    # app = Sw4Lite(translator=Polly("clang"))
    ML4TADASHI.run(Sw4Lite, {"translator": "Polly", "translator_params": "clang++"})


if __name__ == "__main__":
    main()
