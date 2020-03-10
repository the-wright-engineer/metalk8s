@post @local @ci @persistence
Feature: Cluster and Services Configurations
    Scenario: Propagation of Service Configurations to underlying Services
        Given the Kubernetes API is available
        And pods with label 'app.kubernetes.io/name=dex' are 'Ready'
        And we have 2 running pod labeled 'app.kubernetes.io/name=dex' in namespace 'metalk8s-auth' on node 'bootstrap'
        And we have a 'metalk8s-dex-config' ConfigMap with replicas count '2'
        When I update the replicas count to '3'
        And I apply a salt-state to propagate the changes to Dex Service
        Then we have '3' available Deployments for the Dex app

