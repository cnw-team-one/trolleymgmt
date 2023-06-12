import ast
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from web.variables.variables import AWS, GCP

GITHUB_ACTIONS_ENV_FILE = os.environ.get('GITHUB_ENV', None)


def main(incoming_string: str = '', provider: str = ''):
    print(f'incoming_string is: {incoming_string}')
    encoded_content = ast.literal_eval(incoming_string)
    print(f'encoded content is: {encoded_content}')
    eks_subnets = ''
    zone_names = ''
    zone_name = ''
    gcp_project_id = ''
    gke_machine_type = ''
    image_type = ''
    eksctl_object = ''
    project_name = 'trolley-dev'
    if provider == AWS:
        eks_subnets = encoded_content['subnets']
        zone_names = encoded_content['zone_names']
        eksctl_object = encoded_content['eksctl_object']
        print(f'eks_subnets is: {eks_subnets}')
        print(f'eksctl_object is: {eksctl_object}')
    elif provider == GCP:
        zone_name = encoded_content['zone_name']
        gcp_project_id = encoded_content['gcp_project_id']
        gke_machine_type = encoded_content['gke_machine_type']
        image_type = encoded_content['image_type']
        print(f'gke_machine_type is: {gke_machine_type}')
        print(f'gcp_project_id is: {gcp_project_id}')

    cluster_name = encoded_content['cluster_name']
    user_name = encoded_content['user_name']
    cluster_version = encoded_content['cluster_version']
    region_name = encoded_content['region_name']
    num_nodes = encoded_content['num_nodes']
    expiration_time = encoded_content['expiration_time']
    print(f'cluster_name is: {cluster_name}')
    print(f'user_name is: {user_name}')
    print(f'cluster_version is: {cluster_version}')
    print(f'region_name is: {region_name}')
    print(f'zone_name is: {zone_name}')
    print(f'image_type is: {image_type}')
    print(f'num_nodes is: {num_nodes}')
    print(f'expiration_time is: {expiration_time}')
    print(f'project_name is: {project_name}')

    with open(GITHUB_ACTIONS_ENV_FILE, "w") as myfile:
        myfile.write(f"GCP_PROJECT_ID={gcp_project_id}\n")
        myfile.write(f"PROJECT_NAME={project_name}\n")
        myfile.write(f"CLUSTER_NAME={cluster_name}\n")
        myfile.write(f"USER_NAME={user_name}\n")
        myfile.write(f"CLUSTER_VERSION={cluster_version}\n")
        myfile.write(f"GKE_MACHINE_TYPE={gke_machine_type}\n")
        myfile.write(f"REGION_NAME={region_name}\n")
        myfile.write(f"ZONE_NAME={zone_name}\n")
        myfile.write(f"ZONE_NAMES={zone_names}\n")
        myfile.write(f"EKS_SUBNETS={eks_subnets}\n")
        myfile.write(f"IMAGE_TYPE={image_type}\n")
        myfile.write(f"NUM_NODES={num_nodes}\n")
        myfile.write(f"EKSCTL_OBJECT={eksctl_object}\n")
        myfile.write(f"EXPIRATION_TIME={expiration_time}\n")

    with open(GITHUB_ACTIONS_ENV_FILE, "r") as myfile:
        lines = myfile.readlines()
        print(lines)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--incoming_string', default='', type=str,
                        help='The stringified JSON of all the requested parameters')
    parser.add_argument('--provider', default='gcp', type=str, help='The Cloud Provider')
    args = parser.parse_args()
    main(incoming_string=args.incoming_string, provider=args.provider)
