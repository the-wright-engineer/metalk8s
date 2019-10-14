include:
  - .installed

Delay after etcd pod deployment:
  module.wait:
    - test.sleep:
      - length: 10
    - watch:
      - metalk8s: Create local etcd Pod manifest

Waiting for etcd running:
  http.wait_for_successful_query:
    - name: https://127.0.0.1:2379/health
    - verify_ssl: True
    - ca_bundle: /etc/kubernetes/pki/etcd/ca.crt
    - cert:
      - /etc/kubernetes/pki/etcd/server.crt
      - /etc/kubernetes/pki/etcd/server.key
    - status: 200
    - match: '{"health":"true"}'
    - require:
      - module: Delay after etcd pod deployment
