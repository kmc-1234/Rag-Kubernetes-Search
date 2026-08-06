# Runbook: PersistentVolumeClaim Pending

When a PersistentVolumeClaim remains in Pending, first describe the PVC and inspect events.

Check whether a matching StorageClass exists, whether dynamic provisioning is enabled, whether the requested access mode is supported, and whether there is enough available storage.

Also verify that the CSI driver or storage provisioner is healthy and that no namespace quota prevents volume creation.
