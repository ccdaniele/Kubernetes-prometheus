## Kube Main Commands

- List all running pods

    ``` bash
    $ kubectl get pods
    ```

    or

    ``` bash
    $ kubectl get pods --all-namespaces
    ```

- Apply changes after editing values.yaml file

    ``` bash
    $ helm upgrade -f values.yaml <release_name> --set datadog.apiKey=<api_key> datadog/datadog --set targetSystem=linux  
    ```

- Install / apply changes after editing a integration .yaml file

    ``` bash
    $ kubectl apply -f <file_name>.yaml
    ```

- Generate a flare or status for the pod / cluster agent

    ``` bash
    $ kubectl exec <pod_name> -it agent <agent_command> (status or flare)
    ```

- Extract flare from local container

    ``` bash
    $ kubectl cp <namespace/pod_name>:<generated_URL> <local_machine_directory>/<flare_new_name>.zip -c agent
    ```

Example:

``` bash
$ kubectl cp default/release-datadog-x7d7h:/tmp/datadog-agent-2022-06-06T16-31-22Z.zip Flares/flare.zip -c agent
```

### More information

- [Helm Documentation](https://helm.sh/)
- [Kubectl Cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Datadog values.yaml](https://github.com/DataDog/helm-charts/blob/main/charts/datadog/values.yaml)
