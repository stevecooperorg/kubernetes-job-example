This is an as-yet-non-functional attempt to build a python work processor, using rabbitmq to store the work to be 
done, and executing as a kubernetes job so that you can load up rabbit, start the job, and things should process 
across all pods and then termnate when there's no more work to do.

It has several parts

- a loader (`./loader`) which puts "0".."99" into rabbitmq
- a processor (`./processor`) which should pull items off the queue and call a callback function for each id
- Dockerfiles
- Kubernetes manifests (`./kubernetes`) to set up rabbit (work-queue.yaml), to load the IDs (load.yaml) and to 
  process the items (job.yaml)

The work queue and the loader works; the processor just sorta sits there doing nothing. That's probably my terrible 
python skills.



To see this in action;

build the image and push it to a docker repo (see Makefile, docker-push target, for how to push to public docker hub 
for non-sensitive images)

Then assuming you have command-line access to kubernetes, in a terminal window;

1. Create a namespace where we can run the job;

```
kubectl create namespace batch-job-example
```

2. switch to use that namespace by default:

```
kubectl config set-context --current --namespace=batch-job-example
```

3. Deploy rabbitmq to serve as a work queue
```
kubectl -f kubernetes/work-queue.yaml
```   

4. Create a secret to hold your username and password:
```
kubectl create secret generic aws-credential-secret \
  --from-literal=JOB_USER=my-user \
  --from-literal=JOB_PASS=my-pass 
```

5. Modify `./kubernetes/job.yaml` to fill in any extra details like docker image or degree of parallelism

6. if you're re-running, delete any old jobs running in the cluster;

```
kubectl delete job my-batch-job
```

7. run the job

```
kubectl apply -f kubernetes/job.yaml
```

8. see the status of the job itself;

```
kubectl describe job my-batch-job 
```

9. see the containers being spun up by the job

```
kubectl get pods -l job-name=my-batch-job

NAME                 READY   STATUS      RESTARTS   AGE
my-batch-job-crf27   0/1     Completed   0          106s
```

10. see the logs of one pod in the batch;

```
kubectl logs my-batch-job-crf27
```