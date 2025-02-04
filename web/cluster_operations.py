import getpass
import logging
import os
import platform
import sys
from dataclasses import asdict

import requests
from dotenv import load_dotenv

from variables.variables import GKE, ZONE_NAME, EKS, REGION_NAME
from mongo_handler.mongo_utils import retrieve_cluster_details
from mongo_handler.mongo_objects import EKSCTLNodeGroupObject, EKSCTLObject, EKSCTLMetadataObject

DOCKER_ENV = os.getenv('DOCKER_ENV', False)

log_file_name = 'server.log'
if DOCKER_ENV:
    log_file_path = f'{os.getcwd()}/web/{log_file_name}'
else:
    log_file_path = f'{os.getcwd()}/{log_file_name}'

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(filename=log_file_path)
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

project_folder = os.path.expanduser(os.getcwd())
load_dotenv(os.path.join(project_folder, '.env'))

# horrible hack to solve the Dockerfile issues. Please find a better solution
run_env = 'not_github'
try:
    github_env_something = os.getenv('GITHUB_ENV')
    if github_env_something is not None:
        run_env = 'github'
        logger.info('this runs on github')
    else:
        logger.info('this does not run on github')
except:
    run_env = 'not github'
    logger.info('this does not run on github')

if 'Darwin' in platform.system() or run_env == 'github':
    AWS_CREDENTIALS_PATH = f'/Users/{getpass.getuser()}/.aws/credentials'
else:
    AWS_CREDENTIALS_PATH = '/home/app/.aws/credentials'


class ClusterOperation:
    def __init__(self, provider: str = "", user_email: str = "", github_actions_token: str = "",
                 github_repository: str = "", user_name: str = "", project_name: str = "", cluster_name: str = "",
                 cluster_type: str = "", cluster_version: str = "", aks_location: str = "",
                 region_name: str = "", zone_name: str = "", gcp_project_id: str = "", gke_machine_type: str = "",
                 gke_region: str = "", gke_zone: str = "", eks_machine_type: str = "",
                 eks_volume_size: int = "",
                 eks_location: str = "", eks_zones: str = "", num_nodes: int = "", image_type: str = "",
                 expiration_time: int = 0, discovered: bool = False, mongo_url: str = "",
                 mongo_password: str = "", mongo_user: str = "", trolley_server_url: str = "",
                 aws_access_key_id: str = "", aws_secret_access_key: str = "", google_creds_json: str = "",
                 azure_credentials: str = ""):
        self.mongo_url = mongo_url
        self.mongo_password = mongo_password
        self.mongo_user = mongo_user
        self.trolley_server_url = trolley_server_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.google_creds_json = google_creds_json
        self.azure_credentials = azure_credentials
        self.cluster_name = cluster_name
        self.user_name = user_name
        self.project_name = project_name
        self.github_actions_token = github_actions_token
        self.github_repository = github_repository
        self.cluster_type = cluster_type
        self.cluster_version = cluster_version
        self.aks_location = aks_location
        self.region_name = region_name
        self.zone_name = zone_name
        self.eks_machine_type = eks_machine_type
        self.eks_volume_size = eks_volume_size
        self.gcp_project_id = gcp_project_id
        self.gke_machine_type = gke_machine_type
        self.gke_region = gke_region
        self.gke_zone = gke_zone
        self.eks_zones = eks_zones
        self.eks_location = eks_location
        self.num_nodes = num_nodes
        self.image_type = image_type
        self.expiration_time = expiration_time
        self.discovered = discovered
        self.eksctl_object_dict = {}

        self.github_action_request_header = {
            'Content-type': 'application/json',
            'Accept': 'application/vnd.github+json',
            'Authorization': f'token {self.github_actions_token}'
        }
        self.github_actions_api_url = f'https://api.github.com/repos/{self.github_repository}/dispatches'
        self.github_test_url = f'https://api.github.com/repos/{self.github_repository}'

    def build_eksctl_object(self):
        eksctl_node_groups_object = EKSCTLNodeGroupObject(name='ng1', instanceType=self.eks_machine_type,
                                                          desiredCapacity=int(self.num_nodes),
                                                          volumeSize=int(self.eks_volume_size))
        eksctl_metadata = EKSCTLMetadataObject(name=self.cluster_name, region=self.eks_location)
        metadata: EKSCTLMetadataObject
        node_groups: [EKSCTLNodeGroupObject]
        eksctl_object = EKSCTLObject(apiVersion="eksctl.io/v1alpha5", kind="ClusterConfig", metadata=eksctl_metadata,
                                     nodeGroups=[eksctl_node_groups_object])
        self.eksctl_object_dict = asdict(eksctl_object)

    def get_aws_credentials(self) -> tuple:
        if self.aws_access_key_id and self.aws_secret_access_key:
            return self.aws_access_key_id, self.aws_secret_access_key
        else:
            try:
                with open(AWS_CREDENTIALS_PATH, "r") as f:
                    aws_credentials = f.read()
                    aws_access_key_id = aws_credentials.split('\n')[1].split(" = ")[1]
                    aws_secret_access_key = aws_credentials.split('\n')[2].split(" = ")[1]
                    return aws_access_key_id, aws_secret_access_key
            except Exception as e:
                logger.warning('AWS credentials were not found')

    def github_check(self) -> bool:
        response = requests.get(url=self.github_test_url,
                                headers=self.github_action_request_header)
        if response.status_code == 200:
            return True
        else:
            logger.info(f'This is the request response: {response.reason}')
            return False

    def trigger_gke_build_github_action(self) -> bool:
        encoded_data = {
            "gcp_project_id": self.gcp_project_id,
            "project_name": self.project_name,
            "cluster_name": self.cluster_name,
            "user_name": self.user_name,
            "cluster_version": self.cluster_version,
            "gke_machine_type": self.gke_machine_type,
            "region_name": self.gke_region,
            "zone_name": self.gke_zone,
            "image_type": self.image_type,
            "num_nodes": str(self.num_nodes),
            "expiration_time": self.expiration_time
        }
        json_data = {
            "event_type": "gke-build-api-trigger",
            "client_payload": {
                "google_creds_json": self.google_creds_json,
                "payload": str(encoded_data)
            }
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False

    def trigger_eks_build_github_action(self) -> bool:
        aws_access_key_id, aws_secret_access_key = self.get_aws_credentials()
        encoded_data = {
            "cluster_name": self.cluster_name,
            "project_name": self.project_name,
            "user_name": self.user_name,
            "cluster_version": self.cluster_version,
            "region_name": self.eks_location,
            "num_nodes": str(self.num_nodes),
            "expiration_time": self.expiration_time,
            "eksctl_deployment_file": self.eksctl_object_dict
        }
        json_data = {
            "event_type": "eks-build-api-trigger",
            "client_payload": {
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "payload": str(encoded_data)
            }
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False

    def trigger_aks_build_github_action(self) -> bool:
        json_data = {
            "event_type": "aks-build-api-trigger",
            "client_payload": {"cluster_name": self.cluster_name,
                               "user_name": self.user_name,
                               "cluster_version": self.cluster_version,
                               "aks_location": self.aks_location,
                               "num_nodes": str(self.num_nodes),
                               "azure_credentials": self.azure_credentials,
                               "expiration_time": self.expiration_time}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False

    def trigger_trolley_agent_deployment_github_action(self):
        json_data = {
            "event_type": "trolley-agent-api-deployment-trigger",
            "client_payload": {"cluster_name": self.cluster_name,
                               "cluster_type": self.cluster_type,
                               "zone_name": self.zone_name,
                               "trolley_server_url": self.trolley_server_url,
                               "mongo_user": self.mongo_user,
                               "mongo_password": self.mongo_password,
                               "mongo_url": self.mongo_url}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)

        return response

    def trigger_gcp_caching(self):
        json_data = {
            "event_type": "gcp-caching-action-trigger",
            "client_payload": {"project_name": self.project_name,
                               "google_creds_json": self.google_creds_json,
                               "mongo_user": self.mongo_user,
                               "mongo_password": self.mongo_password,
                               "mongo_url": self.mongo_url}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)

        return response

    def trigger_aws_caching(self):
        json_data = {
            "event_type": "aws-caching-action-trigger",
            "client_payload": {"aws_access_key_id": self.aws_access_key_id,
                               "project_name": self.project_name,
                               "aws_secret_access_key": self.aws_secret_access_key,
                               "mongo_user": self.mongo_user,
                               "mongo_password": self.mongo_password,
                               "mongo_url": self.mongo_url}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)

        return response

    def delete_aks_cluster(self):
        json_data = {
            "event_type": "aks-delete-api-trigger",
            "client_payload": {"cluster_name": self.cluster_name}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False

    def delete_gke_cluster(self):
        gke_cluster_details = retrieve_cluster_details(cluster_type=GKE, cluster_name=self.cluster_name,
                                                       discovered=self.discovered)
        gke_zone_name = gke_cluster_details[ZONE_NAME.lower()]
        print(f'Attempting to delete {self.cluster_name} in {gke_zone_name}')
        json_data = {
            "event_type": "gke-delete-api-trigger",
            "client_payload": {"cluster_name": self.cluster_name,
                               "zone_name": gke_zone_name,
                               "project_name": self.project_name,
                               "google_creds_json": self.google_creds_json}
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False

    def delete_eks_cluster(self):
        eks_cluster_details = retrieve_cluster_details(cluster_type=EKS, cluster_name=self.cluster_name,
                                                       discovered=self.discovered)
        eks_cluster_region_name = eks_cluster_details[REGION_NAME.lower()]
        aws_access_key_id, aws_secret_access_key = self.get_aws_credentials()
        json_data = {
            "event_type": "eks-delete-api-trigger",
            "client_payload":
                {"cluster_name": self.cluster_name,
                 "project_name": self.project_name,
                 "region_name": eks_cluster_region_name,
                 "aws_access_key_id": aws_access_key_id,
                 "aws_secret_access_key": aws_secret_access_key,
                 }
        }
        response = requests.post(self.github_actions_api_url,
                                 headers=self.github_action_request_header, json=json_data)
        logger.info(f'This is the request response: {response}')
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logger.warning(f'This is the request response: {response.reason}')
            return False
