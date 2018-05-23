# mirror-hostess

Modify /etc/hosts file to add record to shadow an external url to point to a kubernetes service

## Configuration

* HOSTS_FILE (default: /etc/hosts)
* HOSTS_FILE_BACKUP (default: /etc/hosts.backup)
* LOCK_FILE (default: /var/lock/mirror-hostess)
* SERVICE_NAME (default: registry-mirror)
* SERVICE_NAMESPACE (default: default)
* SHADOW_FQDN (default: registry.example.com)
