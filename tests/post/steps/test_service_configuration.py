import json
import yaml

import pytest
from pytest_bdd import scenario, given, then, when, parsers

import kubernetes.client
from kubernetes.client import AppsV1Api
from kubernetes.client.rest import ApiException

from tests import kube_utils
from tests import utils


# Constants {{{


BODY = """
data:
  config.yaml: |-
    apiVersion: addons.metalk8s.scality.com
    kind: DexConfig
    spec:
      deployment:
        replicas: 3
      localuserstore:
        enabled: true
        userlist:
          - email: "admin@metalk8s.invalid"
            hash: "$2a$10$2b2cU8CPhOTaGrs1HRQuAueS7JTT5ZHsHSzYiFPm1leZck7Mc8T4W"
            username: "admin"
            userID: "08a8684b-db88-4b73-90a9-3cd1661f5466"
      connectors: []
"""


# }}}


# Fixtures {{{


@pytest.fixture
def k8s_appsv1_client(k8s_apiclient):
    return AppsV1Api(api_client=k8s_apiclient)


# }}}


# Scenarios {{{


@scenario('../features/service_configuration.feature',
          'Propagation of Service Configurations to underlying Services')
def test_service_config_propagation(host):
    pass


# }}}


# Given {{{


@given(parsers.parse(
    "we have a '{name}' ConfigMap with replicas count '{replicas}'"))
def check_configmap_configuration(
    host,
    k8s_client,
    name,
    replicas
):
    namespace = "metalk8s-auth"
    response = read_namespace_config_map(k8s_client, name, namespace)

    assert response, ("No ConfigMap with name {} found".format(name))

    try:
        response_config_yaml = yaml.safe_load(response.data['config.yaml'])
    except yaml.YAMLError as exc:
        raise Exception(
            'Invalid YAML format in ConfigMap {}: {!s}'.format(name, exc)
        )
    except Exception as exc:
        raise Exception(
            'Failed loading `config.yaml` from ConfigMap {}: {!s}'.format(
                name, exc
            )
        )
    response_replicas = \
        response_config_yaml['spec']['deployment']['replicas']

    assert int(replicas) == response_replicas, (
        "The running service configuration for replica count is {}, while"
        "the expected service configuration value is {}".format(
            response_replicas, replicas)
    )

# }}}


# Given {{{


@when(parsers.parse("I update the replicas count to '{replicas}'"))
def update_replicas_count(host, k8s_client, replicas):
    namespace = "metalk8s-auth"
    name = "metalk8s-dex-config"
    # This patch here overrides the entire config.yaml
    try:
        response = k8s_client.patch_namespaced_config_map(
            name, namespace, yaml.safe_load(BODY)
        )
    except Exception as exc:
        pytest.fail("Unable to patch ConfigMap with error: {}".format(exc))
    assert response

    read_patch_configmap = read_namespace_config_map(
        k8s_client, name, namespace
    )

    try:
        config_yaml = yaml.safe_load(
            read_patch_configmap.data['config.yaml']
        )
    except yaml.YAMLError as exc:
        raise Exception(
            'Invalid YAML format in ConfigMap {}: {!s}'.format(name, exc)
        )
    except Exception as exc:
        raise Exception(
            'Failed loading `config.yaml` from ConfigMap {}: {!s}'.format(
                name, exc
            )
        )

    patched_replicas = config_yaml['spec']['deployment']['replicas']

    assert int(replicas) == patched_replicas, (
        "The service configuration for replica count is {}, while the"
        "new expected service configuration value is {}".format(
            patched_replicas, replicas)
    )

# When {{{


@when("I apply a salt-state to propagate the changes to Dex Service")
def apply_service_config(host, version, request):
    ssh_config = request.config.getoption('--ssh-config')
    command = (
        "salt-run state.sls metalk8s.addons.dex.deployed saltenv=metalk8s-{}"
        .format(version)
    )

    with host.sudo():
        output = host.run(
            'kubectl --kubeconfig=/etc/kubernetes/admin.conf '
            'exec --namespace kube-system salt-master-bootstrap %s',
            command,
        )

        assert output.rc == 0, output.stdout
        # if output.rc != 0:
        #     pytest.fail(
        #         "Cannot execute command in container {}".format(output.stderr)
        #     )


# }}}


# Then {{{



@then(parsers.parse("we have '{count}' available Deployments for the Dex app"))
def get_deployments(host, k8s_appsv1_client, count):
    name = "dex"
    namespace = "metalk8s-auth"

    try:
        response = k8s_appsv1_client.read_namespaced_deployment(
            name=name, namespace=namespace
        )
    except Exception as exc:
        pytest.fail("Unable to read Dex Deployment with error: {}".format(
            exc)
        )

    assert response.status.available_replicas == int(count), (
        "Dex Deployment has {} replicas, mean while we expected {}".format(
            response.status.available_replicas, count
        )
    )


# }}}


# Helpers {{{


def read_namespace_config_map(k8s_client, name, namespace):
    try:
        response = k8s_client.read_namespaced_config_map(
            name, namespace
        )
    except Exception as exc:
        pytest.fail(
            "Unable to read {} ConfigMap with error: {!s}".format(name, exc)
        )

    return response

# }}}