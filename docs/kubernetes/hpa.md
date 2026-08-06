# Horizontal Pod Autoscaler

The Horizontal Pod Autoscaler changes the number of Pod replicas based on observed metrics such as CPU utilization, memory usage, or custom metrics.

HPA watches metrics, compares them with the configured target, and updates the replica count on a scalable resource such as a Deployment or StatefulSet.

If HPA is not scaling, check metrics-server availability, resource requests, target metrics, and events on the HPA object.
