import json

import click

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS
from fovus.util.util import Util


@click.command("pre-config-resources")
@click.option("--pipeline-id", type=str, help="The ID of the pipeline to configure the resource for.")
@click.option(
    "--configurations", type=str, help="A JSON-like string representing the resource configurations for the pipeline."
)
def pipeline_pre_config_resources_command(pipeline_id: str, configurations: str):
    """
    Pre-configure the resource for a pipeline based on the configurations.
    """
    print("Authenticating...")
    fovus_api_adapter = FovusApiAdapter()
    print("Configuring pipeline resource...")
    configurations_dict = json.loads(configurations)
    response = fovus_api_adapter.pre_config_resources(
        {"pipelineId": pipeline_id, "configurations": configurations_dict}
    )
    Util.print_success_message(GENERIC_SUCCESS)
    print(response)
