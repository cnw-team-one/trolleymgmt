from dataclasses import dataclass
from bson import ObjectId


@dataclass
class UserObject:
    first_name: str
    last_name: str
    user_name: str
    hashed_password: str
    team_name: str
    user_email: str
    profile_image_id: ObjectId = ObjectId()


@dataclass
class GKEObject:
    cluster_name: str
    user_name: str
    kubeconfig: str
    nodes_names: list
    nodes_ips: list
    created_timestamp: int
    human_created_timestamp: str
    expiration_timestamp: int
    human_expiration_timestamp: str
    project_name: str
    zone_name: str
    cluster_version: str
    runtime_version: str
    os_image: str
    region_name: str
    availability: bool = True


@dataclass
class GKEAutopilotObject:
    cluster_name: str
    user_name: str
    kubeconfig: str
    nodes_names: list
    nodes_ips: list
    created_timestamp: int
    human_created_timestamp: str
    expiration_timestamp: int
    human_expiration_timestamp: str
    project_name: str
    zone_name: str
    cluster_version: str
    region_name: str
    availability: bool = True


@dataclass
class EKSObject:
    cluster_name: str
    user_name: str
    kubeconfig: str
    nodes_names: list
    nodes_ips: list
    created_timestamp: int
    human_created_timestamp: str
    expiration_timestamp: int
    human_expiration_timestamp: str
    project_name: str
    zone_name: str
    region_name: str
    cluster_version: str
    availability: bool = True


@dataclass
class AKSObject:
    cluster_name: str
    user_name: str
    kubeconfig: str
    nodes_names: list
    nodes_ips: list
    resource_group: str
    created_timestamp: int
    human_created_timestamp: str
    expiration_timestamp: int
    human_expiration_timestamp: str
    zone_name: str
    region_name: str
    cluster_version: str
    availability: bool = True


@dataclass
class GKECacheObject:
    zones_list: list
    machine_types_dict: dict
    regions_list: list
    versions_list: list
    gke_image_types: list
    regions_zones_dict: dict


@dataclass
class EKSCacheObject:
    zones_list: list
    regions_list: list
    subnets_dict: dict
    regions_zones_dict: dict


@dataclass
class AKSCacheObject:
    locations_dict: dict


@dataclass
class HelmCacheObject:
    helms_installs: list


@dataclass
class DeploymentYAMLObject:
    cluster_type: str
    cluster_name: str
    deployment_yaml_dict: dict
