install kubectl to control you kubernetes cluster

``` bash
brew install kubernetes-cli
```

install minikube

``` bash
brew install minikube
```

installing helm

``` bash
brew install helm
```

start minikube, this will create a single node kubernetes cluster on your machine

``` bash
minikube start
```

see all the pods running in the default namespace, you will see all the underlaying components that make up a kubernetes cluster

``` bash
kubectl get pods --all-namespaces
```

list the minikube profiles (environments)

``` bash
minikube profile list
```

Note that if you wanted to create a new profile

``` bash
minikube start -p <profile_name>
```

Other minikube commands

``` bash
minikube stop
minikube status
minikube delete -p <profile_name>
```

connect to minikube

``` bash
minikube ssh
```

Lets install the agent in this cluster, you can do this two ways, one with Helm or with a Daemonset. A Daemonset will make sure to install an agent in every node in this case 1 because we have 1 node. Helm is an extra layer over Kubernetes that is easier to setup.

Link to the Basic Helm chart for the agent:
https://raw.githubusercontent.com/DataDog/helm-charts/master/charts/datadog/values.yaml

Helm is also similar to a package manage but for helm charts so you can add repositories that it can pull from. If it's your first time installing it, then your helm wouldn't have any repositories saved. 

You can check what repositories your helm command has saved

``` bash
helm repo list
```

Install the datadog helm repo and the helm stable 

``` bash
helm repo add datadog https://helm.datadoghq.com
helm repo add stable https://charts.helm.sh/stable
```

Make sure the chart repos are up to date

``` bash
helm repo update
```

running the agent helm chart to deploy it on your minikube
target system pertains to what kind of containers you are running linux or windows

``` bash
helm install <RELEASE_NAME> -f values.yaml  --set datadog.apiKey=<DATADOG_API_KEY> datadog/datadog --set targetSystem=<TARGET_SYSTEM>
```

my command:

``` bash
helm install python-release -f values.yaml --set datadog.apiKey=$DD_API_KEY datadog/datadog --set targetSystem=linux
```

now if you run 

``` bash
kubectl get pods

# OUTPUT
NAME                                                    READY   STATUS    RESTARTS   AGE
python-release-datadog-cluster-agent-69ff7b894f-tbq65   1/1     Running   0          2m59s
python-release-datadog-z9d9j                            2/3     Running   0          2m59s
python-release-kube-state-metrics-94ddd7b89-6664c       1/1     Running   0          2m59s
```

python-release-xxx is the agent pod, here there are 2 containers running, the agent container and the process agent. If APM and systemprobe were enabled, they would also be in this pod.
python-release-cluster-agent-xxx is the cluster agent...
python-release-kube-state-metrics-xxx the is the pod for KSM kubernetes state metrics used to collect kubernetes_state.* Link: https://docs.datadoghq.com/containers/kubernetes/data_collected/#kubernetes-state

If you dont see the KSM pod then it might be because `KubeStateMetricsCore` is enabled in which case it wouldn't because this is now handled by the cluster agent.
KB about their differences: https://datadoghq.atlassian.net/wiki/spaces/TS/pages/2078311568/Understand+and+troubleshoot+Kubernetes+State+Metrics+and+KSM+Core+tickets

All of the kubernetes.* metrics are being collected from the kubelet component which is managed by kubernetes running on every node and the kubernetes_state.* metrics collected by the KSM node in this case.

The KMS pod isn't specific to Datadog, it is possible that they already had one deployed but our chart deploys it by default incase they didn't have one running.

lets check if the kubelet and KSM checks are running as expected. if the kubelet check fails with the `Unable to detect kubelet url...` the you will need to update the `datadog.kubelet.tlsVerify` option to `false` then redeploy and run the status command again

``` bash
kubectl exec -it <agent_pod_name> agent status
```

redeploy with

``` bash
helm upgrade ...
```

You should now be able to see kubernetes metrics begin to come into datadog, note that the agent will is able to retrieve pods from every namespace not only from its own

you can list your deployed charts with 

``` bash
helm list
```

you can stop a deployed chart with 

``` bash
helm uninstall <release_name>
```

## Configuring an Integration

you can configure an integration in kubernetes in two ways annotations which is configured on the pod side or configmap which is configured on the agent side

### Annotations

In this example we will try to configure a redis integration, lets create a `redis.yaml` file with the content below:

``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis
  annotations:
    ad.datadoghq.com/redis.check_names: '["redisdb"]'
    ad.datadoghq.com/redis.init_configs: '[{}]'
    ad.datadoghq.com/redis.instances: |
      [
        {
          "host": "%%host%%",
          "port":"6379"
        }
      ]      
  labels:
    name: redis
spec:
  containers:
    - name: redis
      image: redis
      ports:
        - containerPort: 6379
```

Notice that we added 3 annotations to configure the redis integraton

``` yaml
annotations:
ad.datadoghq.com/redis.check_names: '["redisdb"]'
ad.datadoghq.com/redis.init_configs: '[{}]'
ad.datadoghq.com/redis.instances: |
    [
    {
        "host": "%%host%%",
        "port":"6379"
    }
    ]      
```

Notice that the `init_configs` and `instances` sections are the same as the configurations you find in a non containerized environment link to redis one: https://github.com/DataDog/integrations-core/blob/master/redisdb/datadog_checks/redisdb/data/conf.yaml.example

One thing to note is that the `container_identifier` (`metadata.name`) is `redis` this needs to match with the value in `spec.containers.name`.

Since we are deploying a custom yaml file we can't use helm we need to deploy it using kubectl

``` bash
kubectl apply -f redis.yaml
```

Now after having the redis pod running and the agent deployed, the agent would auto discover the redis pod and begin running checks on it.

run the agent status command and check the redisdb integration

``` bash
kubectl exec -it <agent_pod> agent status
```

for most integrations, the agent has a `auto_conf.yaml` file that will be automatically used if it finds a pod running a specific image. For such integrations, if no annotations are provide like we did for the redis pod here, the agent would still be able to detect it and will use the configurations found in the `auto_conf.yaml`. In the status displayed for the redisdb check we can see that there is a line called `Configuration Source`, this will give you a hint whether the agent used the `auto_conf.yaml` file or if annotations on the pod was used (if you see the container id listed instead of a file). if both are present then the annotations will take president. You can find a list of the integrations we have an `auto_conf.yaml` for: https://docs.datadoghq.com/agent/guide/auto_conf/#pagetitle

If for whatever reason the customer would like to disable the `auto_conf.yaml` because they don't want to collect related metrics, they can use the `DD_IGNORE_AUTOCONF`environment variable in the `datadog.env` section of the `values.yaml` file you would need to use the `DD_IGNORE_AUTOCONF` environment variable and then provide a string with a list of integrations you would like the agent to ignore. in this case:

``` yaml
envs:
    - name: DD_IGNORE_AUTOCONF
      values: "redisdb"
```

After doing this and redeploying the agent, you will see that the redisdb check fails as no check is happening. https://docs.datadoghq.com/agent/guide/auto_conf/#disabling-auto-configuration

### ConfigMap

Now lets configure redis by adding the configuration on the agent side. Leave the redis pod without annotations but now we create a file called `redisConfigMap.yaml` and insert the following:

``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redisdb-config-map
  namespace: default
data:
  redisdb-config: |-
    ad_identifiers:
      - redis
    init_config:
    instances:
      - host: "%%host%%"
        port: "6379" 
```

Somethings to note are that in the `metadata.name` section you can see that it is `<name_of_check>-config` also the `ad_identifier` must match the value if the container short image, more info of `ad_indentifiers` https://docs.datadoghq.com/agent/guide/ad_identifiers/. In the config section you pretty much would put what you wouldve used in the standard datadog.yaml.

now we can deploy this configmap

``` bash
kubectl apply -f redisConfigMap.yaml
```

now that its been deployed we need to mount it to the Agent pod using volumes and volumeMounts, in you `values.yaml` file you can mount them like this the `agents.volumes` and then the `agent.volumeMounts`.

``` yaml
volumes: 
- name: redisdb-config-map
    configMap:
    name: redisdb-config-map
    items:
        - key: redisdb-config
        path: conf.yaml
```

once these changes are out of the way you can redeploy the agent and lets check what is in the `redisdb.d` directory now in the agent

``` bash
kubectl exec -it <agent_pod> cat /etc/datadog-agent/conf.d/redisdb.d/conf.yaml
```

you should see exactly what was put in the `data.redisdb-config`, now lets look at what the `Configuration Source` says

``` bash
kubectl exec -it <agent_pod> agent check redisdb
```

we should now see that the file its using as the configuration is the conf.d file that the configMap created now. an alternative way of configuring the agent would but by adding the configurations directly in the `values.yaml` file. To do this you will need to go to the `datadog.confd` section in the `values.yaml` file and put in the following:

``` yaml
confd:
  redisdb.yaml: |-
    ad_identifiers:
      - redis
    init_config:
    instances:
      - host: "%%host%%"
        port: "6379"
```

notice how this is almost exactly like the configMap but doesn't require another file to be created, deployed then mounted on the agent, you put it in the `values.yaml` file and done. to test this, remove the volume changes we made to the `values.yaml` file, make the confd changes and then redeploy the agent.

now when you run the redisdb check you will see that the configuration file being used is called redisdb.yaml
