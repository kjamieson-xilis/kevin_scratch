import pprint

import kubernetes as k8s

PP = pprint.PrettyPrinter(indent=2)

def main():
    k8s.config.load_kube_config()
    v1 = k8s.client.CoreV1Api()
    print("Listing nodes:")
    ret = v1.list_node(watch=False)
    for i in ret.items:
        instance_type = i.metadata.labels['node.kubernetes.io/instance-type']
        name = i.metadata.name
        cap_pods = i.status.capacity['pods']
        allocatable_pods = i.status.allocatable['pods']
        cap_cpu = i.status.capacity['cpu']
        allocatable_cpu = i.status.allocatable['cpu']
        print(name, instance_type)
        #print(f"{i.metadata.namespace}\t{i.metadata.name}\t{i.spec.node_selector}")
        #if 'modelserver' in i.metadata.name:
            #PP.pprint(i)

            #print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))



if __name__ == '__main__':
    main()
