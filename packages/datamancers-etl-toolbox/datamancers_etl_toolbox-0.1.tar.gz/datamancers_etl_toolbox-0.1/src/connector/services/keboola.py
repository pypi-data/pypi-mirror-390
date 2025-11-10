import requests
import json
import argparse
import logging
import time
import yaml

logging.basicConfig(level=logging.INFO)


class KeboolaClient:
    def __init__(self, token, region="north-europe.azure"):
        self.token = token
        self.region = region
        self.base_url = f"https://connection.{region}.keboola.com/v2/storage"
        self.queue_url = f"https://queue.{region}.keboola.com"
        self.headers = {
            "X-Storageapi-Token": self.token,
            "Content-Type": "application/json",
        }

    # --- Orchestration Job Flow (original logic) ---
    def run_orchestration(self, orchestration_config):
        response = requests.post(
            url=f"{self.queue_url}/jobs",
            json={
                "component": "keboola.orchestrator",
                "config": orchestration_config,
                "mode": "run",
            },
            headers=self.headers,
        )
        if response.status_code == 201:
            response_dict = response.json()
            job_id = response_dict["id"]
            job_url = f"https://connection.{self.region}.keboola.com/admin/projects/{response_dict['project']['id']}/queue/{job_id}"
            logging.info(
                f"Keboola Orchestration with config id {orchestration_config}"
                f" succesfully created with id {response_dict['id']} \n"
                f"See {job_url} to see process in detail"
            )
        else:
            raise Exception(
                f"orchestration job of configuration:{orchestration_config} has not been created. \n"
                f"Status Code: {response.status_code} \n"
                f"Message: {response.text}"
            )

        response_dict = {"status": "processing"}
        while response_dict["status"] in ["processing", "created", "waiting"]:
            time.sleep(30)
            response = requests.get(
                url=f"{self.queue_url}/jobs/{job_id}", headers=self.headers
            )
            response_dict = response.json()

        job_status = response_dict["status"]
        if job_status != "success":
            raise Exception(
                f"orchestration job of id:{job_id} has not ended in success. \n"
                f"Message: {response_dict['result']['message']} \n"
                f"See {job_url} for exact reason "
            )
        return response_dict

    # --- Configuration Management Methods ---
    def list_configurations(self, component_id):
        url = f"{self.base_url}/components/{component_id}/configs"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_configuration(self, component_id, config_id):
        url = f"{self.base_url}/components/{component_id}/configs/{config_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update_configuration(self, component_id, config_id, configuration):
        url = f"{self.base_url}/components/{component_id}/configs/{config_id}"
        resp = requests.put(
            url, headers=self.headers, json={"configuration": configuration}
        )
        resp.raise_for_status()
        return resp.json()

    def rollback_configuration(self, component_id, config_id, version_id):
        url = f"{self.base_url}/components/{component_id}/configs/{config_id}/versions/{version_id}/rollback"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def copy_configuration(self, component_id, config_id, version_id, new_name):
        url = f"{self.base_url}/components/{component_id}/configs/{config_id}/versions/{version_id}/copy"
        resp = requests.post(url, headers=self.headers, json={"name": new_name})
        resp.raise_for_status()
        return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Keboola API CLI")
    parser.add_argument("token", help="Keboola Storage API token")
    parser.add_argument("--region", default="north-europe.azure")
    subparsers = parser.add_subparsers(dest="command")

    # Orchestration (original flow)
    orch_parser = subparsers.add_parser("orchestrate", help="Run orchestration job")
    orch_parser.add_argument("orchestration_config")

    # List configs
    list_parser = subparsers.add_parser("list", help="List configurations")
    list_parser.add_argument("component_id")

    # Get config
    get_parser = subparsers.add_parser("get", help="Get configuration detail")
    get_parser.add_argument("component_id")
    get_parser.add_argument("config_id")

    # Update config
    update_parser = subparsers.add_parser("update", help="Update configuration")
    update_parser.add_argument("component_id")
    update_parser.add_argument("config_id")
    update_parser.add_argument("config_json")

    # Rollback config
    rollback_parser = subparsers.add_parser(
        "rollback", help="Rollback configuration to version"
    )
    rollback_parser.add_argument("component_id")
    rollback_parser.add_argument("config_id")
    rollback_parser.add_argument("version_id")

    # Copy config
    copy_parser = subparsers.add_parser(
        "copy", help="Copy configuration version to new config"
    )
    copy_parser.add_argument("component_id")
    copy_parser.add_argument("config_id")
    copy_parser.add_argument("version_id")
    copy_parser.add_argument("new_name")

    args = parser.parse_args()
    client = KeboolaClient(args.token, args.region)

    if args.command == "orchestrate":
        client.run_orchestration(args.orchestration_config)
    elif args.command == "list":
        print(json.dumps(client.list_configurations(args.component_id), indent=2))
    elif args.command == "get":
        print(
            json.dumps(
                client.get_configuration(args.component_id, args.config_id), indent=2
            )
        )
    elif args.command == "update":
        config = json.loads(args.config_json)
        print(
            json.dumps(
                client.update_configuration(args.component_id, args.config_id, config),
                indent=2,
            )
        )
    elif args.command == "rollback":
        print(
            json.dumps(
                client.rollback_configuration(
                    args.component_id, args.config_id, args.version_id
                ),
                indent=2,
            )
        )
    elif args.command == "copy":
        print(
            json.dumps(
                client.copy_configuration(
                    args.component_id, args.config_id, args.version_id, args.new_name
                ),
                indent=2,
            )
        )
    else:
        parser.print_help()


def iterative_configuration_update_and_run(
    region, token, component_id, config_id, config_list
):
    client = KeboolaClient(token, region)
    logging.info(
        f"Component id: {component_id} with configuration id: {config_id} will be updated with following values and run iteratively:\n {config_list}"
    )

    config = client.get_configuration(component_id, config_id)

    for config_item in config_list:
        for key, value in config_item.items():
            config[key] = value
        logging.info(f"Updating configuration {config_id} to {config}")
        client.update_configuration(component_id, config_id, config)
        logging.info(f"Running orchestration {config_id}")
        client.run_orchestration(config_id)
        logging.info(f"Configuration {config_id} has been updated and run successfully")


if __name__ == "__main__":
    with open("configs/svetoleju.yaml", "r") as f:
        config = yaml.safe_load(f)

    iterative_configuration_update_and_run(
        region=config["KEBOOLA"]["REGION"],
        token=config["KEBOOLA"]["TOKEN"],
        component_id=config["KEBOOLA"]["COMPONENT_ID"],
        config_id=config["KEBOOLA"]["CONFIG_ID"],
        config_list=config["KEBOOLA"]["CONFIG_LIST"],
    )
