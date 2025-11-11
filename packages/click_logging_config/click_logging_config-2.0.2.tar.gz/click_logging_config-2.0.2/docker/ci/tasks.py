#  Copyright (c) 2023 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.

import pathlib

import invoke

BUILD_DOCKERFILE = "Dockerfile-apt-lock"


def _find_container_tool(
    context: invoke.Context,
) -> str:
    for this_command in ["nerdctl", "docker", "podman"]:
        try:
            context.run(f"{this_command} --version")
            return this_command
        except invoke.exceptions.UnexpectedExit:
            pass

    raise FileNotFoundError("No container tool found")


@invoke.task
def generate_lockfile(
    context: invoke.Context,
    target: str,
) -> None:
    target_path = pathlib.Path(target)
    lock_file = target_path.with_suffix(".lock")
    if not target_path.suffix:
        src_file = target_path.with_suffix(".txt")
    else:
        src_file = target_path

    docker_image = f"{target_path.stem}".replace("_", "-")

    assert src_file.is_file(), f"File {src_file} does not exist"

    # make sure lock file does not exist
    try:
        lock_file.unlink(missing_ok=True)
    except OSError:
        pass

    container_command = _find_container_tool(context)

    context.run(
        (
            f"{container_command} "
            "build "
            f"--build-arg requirements_src={target_path.stem} "
            "--no-cache "
            f"-t {docker_image} "
            f"-f {BUILD_DOCKERFILE} "
            "."
        ),
        echo=True,
    )
    context.run(
        (
            f"{container_command} "
            "run "
            "--rm "
            "-v $(PWD):/media "
            "-w /media "
            f"{docker_image}"
        ),
        echo=True,
    )
    assert lock_file.is_file(), f"File {lock_file} has not been generated"
