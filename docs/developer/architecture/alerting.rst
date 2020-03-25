Alerting Functionalities
========================

Context
-------

MetalK8s is automatically deploying Prometheus, Alert Manager and a set of
predefined alert rules. In order to leverage Prometheus and Alert Manager
functionalities, we need to explain, in the documentation, how to use it.
In a later stage, those functionalities will be exposed through various
administration and alerting UIs, but for now, we want to provide our
administrator with enough information in order to use very basic alerting
functionalities.

Requirements
____________

As a MetalK8s administrator, I want to list or know the list of alert rules that
are deployed on MetalK8s Prometheus cluster In Order to identify on what
specific rule I want to be alerted

As a MetalK8s administrator, I want to set notification routing and receiver for
a specific alert In order to get notified per when such alert is fired
The important routing to support are email, slack and pagerduty

As a MetalK8s administrator, I want to update thresholds for a specific alert
rule, In order to adapt the alert rule to the specificities and performances of
my platform.

As a MetalK8s administrator, I want to add a new alert rule, In order to
monitor a specific KPI which is not monitored out of the box by MetalK8s

As a MetalK8s administrator, I want to inhibit an alert rule, In order to skip
alerts in which I am not interested

In all cases, when MetalK8s administrator is upgrading the cluster, all
listed customizations should remain.
