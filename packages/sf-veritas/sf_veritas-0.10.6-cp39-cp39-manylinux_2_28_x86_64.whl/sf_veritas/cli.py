import os
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional, Union

from fire import Fire

from .env_vars import SF_DEBUG
from .unified_interceptor import setup_interceptors

METHOD = "os.execvp"


def inject_code(file_path, **kwargs):
    """
    Injects the given code snippet at the top of the target Python file.
    """
    code_to_inject = f"""
from sf_veritas import setup_interceptors

setup_interceptors(
    api_key={kwargs.get('api_key')!r},
    service_identifier={kwargs.get('service_identifier', None)!r},
    service_version={kwargs.get('service_version', None)!r},
    service_additional_metadata={kwargs.get('service_additional_metadata', None)!r},
    profiling_mode_enabled={kwargs.get('profiling_mode_enabled', False)},
    profiling_max_depth={kwargs.get('profiling_max_depth', 5)},
    domains_to_not_propagate_headers_to={kwargs.get('domains_to_not_propagate_headers_to', None)!r},
    site_and_dist_packages_to_collect_local_variables_on={kwargs.get('site_and_dist_packages_to_collect_local_variables_on', None)!r}
)
"""

    # Read the original file content
    with open(file_path, "r") as f:
        original_content = f.read()

    # Combine the injected code with the original content
    new_content = code_to_inject + "\n" + original_content

    # Create a temporary file in the same directory as the original script
    temp_dir = os.path.dirname(file_path)
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, dir=temp_dir, prefix="temp-", suffix=".py"
    )

    # Write the new content to the temporary file
    with open(temp_file.name, "w") as f:
        f.write(new_content)

    return temp_file.name


def get_sf_veritas_index(argv=sys.argv):
    for i, arg in enumerate(argv):
        if "sf-veritas" in arg:
            return i
    return None


def get_python_index(argv=sys.argv):
    if "python" in argv:
        return argv.index("python")
    if "python3" in argv:
        return argv.index("python3")
    return None


def get_command_index(command_name, argv=sys.argv):
    """
    Returns the index of a given command in sys.argv or None if not found.
    """
    if command_name in argv:
        return argv.index(command_name)
    return None


def handle_framework_command(
    command_index,
    module_delimiter=":",
    argv=sys.argv,
    app_path_offset: int = 1,
    **kwargs,
):
    """
    Handles framework commands like uvicorn, gunicorn, sanic, waitress-serve, daphne, etc.
    """
    app_path = argv[command_index + app_path_offset]
    module_path = app_path.split(module_delimiter)[0].replace(".", "/") + ".py"

    # Inject code into the module
    modified_module_path = inject_code(module_path, **kwargs)

    # Turn the modified file path into a dotted module path
    modified_module_relpath = os.path.relpath(modified_module_path, start=os.getcwd())
    new_module_path = os.path.splitext(modified_module_relpath)[0].replace("/", ".")

    # Strip off any leading dots that appear because of ../ or ./ references
    new_module_path = new_module_path.lstrip(".")

    # If there's still nothing, you could do a sanity check here:
    # if not new_module_path:
    #     raise ValueError("Unable to determine a valid module name from path")

    # Reconstruct the final "module:app" string
    if module_delimiter in app_path:
        # e.g., "backend.temp-abcdef:application"
        modified_app_path = (
            new_module_path + module_delimiter + app_path.split(module_delimiter)[1]
        )
    else:
        modified_app_path = new_module_path

    # Build the run_command
    run_command = [argv[command_index], *argv[command_index + 1 :]]
    run_command[app_path_offset] = modified_app_path

    return run_command


def find_application_arg(command_index, argv=sys.argv):
    """
    Finds the application argument for daphne and granian commands, ignoring any flags.
    """
    if SF_DEBUG:
        print(
            f"Checking arguments after index {command_index}: {argv[command_index + 1:]}",
            log=False,
        )
    should_skip = False
    for i in range(command_index + 1, len(argv)):
        if should_skip:
            should_skip = False
            continue
        if argv[i].startswith("-"):
            should_skip = True
            continue
        return argv[i]
    return None


def main(
    api_key: str,
    service_identifier: str = None,
    service_version: Union[str, int] = None,  # Allow both string and int
    service_additional_metadata: Dict[str, Union[str, int, float, None]] = None,
    profiling_mode_enabled: bool = False,
    profiling_max_depth: int = 5,
    domains_to_not_propagate_headers_to: Optional[List[str]] = None,
    site_and_dist_packages_to_collect_local_variables_on: Optional[List[str]] = None,
    *args,
):
    """
    Main function to handle CLI and set up interceptors.

    Args:
        api_key: (Required) API key for authentication. This must be provided as a CLI argument.
        service_identifier: Identifier for the service.
        service_version: Version of the service.
        service_additional_metadata: Additional metadata to associate with the service.
        profiling_mode_enabled: Whether profiling mode is enabled.
        profiling_max_depth: Maximum depth for profiling.
        domains_to_not_propagate_headers_to: Domains to which headers should not be propagated.
        site_and_dist_packages_to_collect_local_variables_on: If set to None, defaults to [], excluding all installed packages.
        *args: Additional command-line arguments to be passed through.
    """

    # Convert service_version to string if it's numeric
    if service_version is not None:
        service_version = str(service_version)

    # Collect setup parameters
    setup_params = {
        "api_key": api_key,
        "service_identifier": service_identifier,
        "service_version": service_version,
        "service_additional_metadata": service_additional_metadata,
        "profiling_mode_enabled": profiling_mode_enabled,
        "profiling_max_depth": profiling_max_depth,
        "domains_to_not_propagate_headers_to": domains_to_not_propagate_headers_to,
        "site_and_dist_packages_to_collect_local_variables_on": site_and_dist_packages_to_collect_local_variables_on,
    }

    # Remaining arguments are captured in *args
    remaining_args = sys.argv[1:]
    try:
        separator_index = sys.argv.index("--")
        remaining_args = sys.argv[separator_index + 1 :]
    except ValueError:
        pass

    if SF_DEBUG:
        print("[[ DEBUG ]] sys.argv [[ /DEBUG ]]", sys.argv)
        print("[[ DEBUG ]] setup_params [[ /DEBUG ]]", setup_params)
        print("[[ DEBUG ]] remaining_args [[ /DEBUG ]]", remaining_args)

    setup_interceptors(**setup_params)

    if not remaining_args:
        print("Usage: sf-veritas [options] <command> [args]")
        sys.exit(1)

    # Detect CLI command and adjust injection based on the framework
    python_index = get_python_index(remaining_args)
    uvicorn_index = get_command_index("uvicorn", remaining_args)
    gunicorn_index = get_command_index("gunicorn", remaining_args)
    flask_index = get_command_index("flask", remaining_args)
    django_admin_index = get_command_index("django-admin", remaining_args)
    sanic_index = get_command_index("sanic", remaining_args)
    pserve_index = get_command_index("pserve", remaining_args)
    waitress_index = get_command_index("waitress-serve", remaining_args)
    daphne_index = get_command_index("daphne", remaining_args)
    granian_index = get_command_index("granian", remaining_args)

    if python_index is not None and python_index >= 0:
        if "-m" in remaining_args:
            module_index = remaining_args.index("-m", python_index)

            # Ensure there's a module specified after `-m`
            if module_index + 1 < len(remaining_args):
                module_dot_path = remaining_args[module_index + 1]
                module_path = module_dot_path.replace(".", "/") + ".py"

                # Inject code into the module, passing setup_params
                modified_module_path = inject_code(module_path, **setup_params)

                # Calculate the relative path for the new temporary file's dot-path
                new_module_dot_path = os.path.splitext(
                    os.path.relpath(modified_module_path, start=os.getcwd())
                )[0].replace("/", ".")

                # Rebuild the command with the modified module dot-path
                code_after_module_index = module_index + 2
                run_command = [
                    sys.executable,
                    "-m",
                    new_module_dot_path,
                ] + remaining_args[code_after_module_index:]
            else:
                print("Error: No module specified after '-m'.")
                sys.exit(1)
        else:
            script_path = remaining_args[python_index + 1]

            # Inject code into the script file directly, passing setup_params
            modified_script_path = inject_code(script_path, **setup_params)

            # Rebuild the command to use the path to the modified script file
            run_command = [sys.executable, modified_script_path] + remaining_args[
                python_index + 2 :
            ]
    elif uvicorn_index is not None:
        run_command = handle_framework_command(
            uvicorn_index, module_delimiter=".", argv=remaining_args, **setup_params
        )
    elif gunicorn_index is not None:
        run_command = handle_framework_command(
            gunicorn_index, argv=remaining_args, **setup_params
        )
    elif sanic_index is not None:
        run_command = handle_framework_command(
            sanic_index, module_delimiter=".", argv=remaining_args, **setup_params
        )
    elif waitress_index is not None:
        run_command = handle_framework_command(
            waitress_index, module_delimiter=":", argv=remaining_args, **setup_params
        )
    elif flask_index is not None:
        # Flask expects the FLASK_APP environment variable
        app_path = os.environ.get("FLASK_APP", None)
        if app_path:
            module_path = app_path.replace(".", "/") + ".py"

            # Inject code into the module, passing setup_params
            modified_module_path = inject_code(module_path, **setup_params)

            # Set the modified path back to FLASK_APP
            os.environ["FLASK_APP"] = modified_module_path.replace("/", ".").replace(
                ".py", ""
            )

        run_command = remaining_args
    elif django_admin_index is not None:
        # Handle django-admin commands
        script_path = remaining_args[django_admin_index]

        # Inject code into the script file directly, passing setup_params
        modified_script_path = inject_code(script_path, **setup_params)

        # Rebuild the command to use the path to the modified script file
        run_command = (
            remaining_args[:django_admin_index]
            + [modified_script_path]
            + remaining_args[django_admin_index + 1 :]
        )
    elif daphne_index is not None or granian_index is not None:
        command_index = daphne_index if daphne_index is not None else granian_index
        app_arg = find_application_arg(command_index, argv=remaining_args)
        app_path_offset = remaining_args.index(app_arg)

        if not app_arg:
            print("Error: No application module specified for daphne or granian.")
            sys.exit(1)

        run_command = handle_framework_command(
            command_index,
            module_delimiter=":",
            argv=remaining_args,
            app_path_offset=app_path_offset,
            **setup_params,
        )
    elif pserve_index is not None:
        # Rebuild the command to use pserve
        run_command = remaining_args
    else:
        # For all other cases, pass the command as-is
        run_command = remaining_args

    if SF_DEBUG:
        print("Run command is now:", run_command, log=False)

    env = os.environ.copy()

    if METHOD == "subprocess.run":
        result = subprocess.run(run_command, env=env)
        sys.exit(result.returncode)
    else:
        os.execvpe(run_command[0], run_command, env)


def fire_main():
    return Fire(main)


if __name__ == "__main__":
    fire_main()
