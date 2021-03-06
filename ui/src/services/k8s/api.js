import { Config } from '@kubernetes/client-node/dist/browser/config';
import { CoreV1Api } from '@kubernetes/client-node/dist/gen/api/coreV1Api';
import { CustomObjectsApi } from '@kubernetes/client-node/dist/gen/api/customObjectsApi';
import { StorageV1Api } from '@kubernetes/client-node/dist/gen/api/storageV1Api';

let config;
let coreV1;
let customObjects;
let storage;

const SOLUTION_CONFIGMAP_NAME = 'metalk8s-solutions';
const APP_K8S_COMPONENT_LABEL = 'app.kubernetes.io/component';

export const updateApiServerConfig = (url, id_token, token_type) => {
  config = new Config(url, id_token, token_type);
  coreV1 = config.makeApiClient(CoreV1Api);
  customObjects = config.makeApiClient(CustomObjectsApi);
  storage = config.makeApiClient(StorageV1Api);
};

export async function getNodes() {
  try {
    return await coreV1.listNode();
  } catch (error) {
    return { error };
  }
}

export async function getPods() {
  try {
    return await coreV1.listPodForAllNamespaces();
  } catch (error) {
    return { error };
  }
}

export async function getKubeSystemNamespace() {
  try {
    return await coreV1.listNamespace(
      null,
      null,
      null,
      'metadata.name=kube-system',
    );
  } catch (error) {
    return { error };
  }
}

export async function createNode(payload) {
  try {
    return await coreV1.createNode(payload);
  } catch (error) {
    return { error };
  }
}

export async function getVolumes() {
  try {
    // We want to change this hardcoded data later
    return await customObjects.listClusterCustomObject(
      'storage.metalk8s.scality.com',
      'v1alpha1',
      'volumes',
    );
  } catch (error) {
    return { error };
  }
}

export async function deleteVolume(deleteVolumeName) {
  try {
    return await customObjects.deleteClusterCustomObject(
      'storage.metalk8s.scality.com',
      'v1alpha1',
      'volumes',
      deleteVolumeName,
      {},
    );
  } catch (error) {
    return error;
  }
}

export async function getPersistentVolumes() {
  try {
    return await coreV1.listPersistentVolume();
  } catch (error) {
    return { error };
  }
}

export async function getStorageClass() {
  try {
    return await storage.listStorageClass();
  } catch (error) {
    return { error };
  }
}

export async function createVolume(body) {
  try {
    return await customObjects.createClusterCustomObject(
      'storage.metalk8s.scality.com',
      'v1alpha1',
      'volumes',
      body,
    );
  } catch (error) {
    return { error };
  }
}

export async function getPersistentVolumeClaims() {
  try {
    return await coreV1.listPersistentVolumeClaimForAllNamespaces();
  } catch (error) {
    return { error };
  }
}

export async function getSolutionsConfigMapForAllNamespaces() {
  try {
    return await coreV1.listConfigMapForAllNamespaces(
      null,
      `metadata.name=${SOLUTION_CONFIGMAP_NAME}`,
    );
  } catch (error) {
    return { error };
  }
}

export async function getUIServiceForAllNamespaces() {
  try {
    return await coreV1.listServiceForAllNamespaces(
      null,
      null,
      null,
      `${APP_K8S_COMPONENT_LABEL}=ui`,
    );
  } catch (error) {
    return { error };
  }
}

export async function getEnvironments() {
  try {
    return await customObjects.listClusterCustomObject(
      'solutions.metalk8s.scality.com',
      'v1alpha1',
      'environments',
    );
  } catch (error) {
    return { error };
  }
}

export async function createEnvironment(body) {
  try {
    return await customObjects.createClusterCustomObject(
      'solutions.metalk8s.scality.com',
      'v1alpha1',
      'environments',
      body,
    );
  } catch (error) {
    return { error };
  }
}

export async function queryPodInNamespace(namespace, podLabel) {
  try {
    return await coreV1.listNamespacedPod(
      namespace,
      null,
      null,
      null,
      null,
      `app=${podLabel}`,
    );
  } catch (error) {
    return { error };
  }
}
