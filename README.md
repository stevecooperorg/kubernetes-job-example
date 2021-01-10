This is an as-yet-non-functional attempt to build a python work processor, using rabbitmq to store the work to be 
done, and executing as a kubernetes job so that you can load up rabbit, start the job, and things should process 
across all pods and then termnate when there's no more work to do.

It has several parts

# work-queue

the work queue is a rabbitmq queue which you can load up with identifiers - in this example you're using a list 
of integers, but it could be a list of files to process, or URLs to download, or whatever you want.

It uses the public rabbitmq docker container, and uses all standard credentials and configurtaions - port 56723, 
user guest, password guest, etc.

To develop locally, you can start the work queue in docker, and it'll be available on `localhost:5672`

```
$ docker run --rm -p 5672:5672 -d --hostname work-queue --name work-queue rabbitmq:3
```

This means you can run python scripts locally, and as long as you tell the scripts to connect to `localhost:5672`, 
the scripts will work.

# loader

The loader is a simple python script which loads the strings "0" to "99" into the queue. This is just for test 
purposes, obviously, and you can adapt the script to load whatever work you want.

To load locally, just run the python file directly, setting your `WORK_QUEUE_HOST` environment variable to 
`localhost`. Under unix:

```
$ export WORK_QUEUE_HOST=localhost && python loader/src/main.py
```

You should see something like

```
$ export WORK_QUEUE_HOST=localhost && python loader/src/main.py
('connecting to work queue ', 'localhost', '5672')
connected to work queue
('loading data:', '0')
('loading data:', '1')
...
('loading data:', '98')
('loading data:', '99')
loaded data
```

# processor

Does the actual work, by grabbing an item from the work queue, doing something with it, and repeating, until there's 
nothing left to do, at which point it quits successfullly (exit code 0). 

The benefit of this approach is that you can run this as a kuberenetes job in a flexible way;

- load up as much work as you want
- start a kubernetes job running as many processors as you want
- the processors will munch through the work queue in parallel
- when the work queue is empty, all the processes will shut down
- when all the processors are empty, the job finishes, so you're not paying any money to keep idle processors running

To run a single processor locally, set the environment variables

```
JOB_USER=<your username>
JOB_PASS=<your password>
WORK_QUEUE_HOST=localhost
```

Then just run the processor script:

```
$ python processor/src/main.py
```

# kubernetes manifests

to run this in kubernetes rather than locally, you need items for each of the things above. 

- `kubernetes/work-queue.yaml` lets you run the rabbitmq work queue in kubernetes. That needs to be running before 
  anything else will work.
- `kubernetes/loader-job.yaml` will run the loader once, then stop
- `kubernetes/process-job.yaml` will run multiple processors, then stop

# Running it locally

- make sure you've got python and docker, and that docker is started
- make sure you've got `pip` installed to manage dependencies
- install `pika` - `pip install pika` ?
- start the rabbitmq - see instructions above
- load it up! - again, instructions above
- run a single processor - instructions above

This should let you develop your scripts nicely

# Running it in kubernetes

1. Build your docker images locally. Two `Dockerfile`s are provided which just pop the python scripts onto an image
```
$ docker build processor -t stevecooperorg/work-queue-processor:latest
$ docker build loader -t stevecooperorg/work-queue-loader:latest
```

2. Publish them to a docker repository. I'm doing it something like this, to publish publicly, but you might want to 
   publish to a private registry like Amazon ECR;

```
$ docker push -t stevecooperorg/work-queue-processor:latest
$ docker push -t stevecooperorg/work-queue-loader:latest
```

3. Make sure you have access to a kubernetes cluster. It's beyond the scope of this example, but you should be able 
   to do this on a terminal;
   
```
$ kubectl get namespace
```

and see a list of kubernetes namespaces, without seeing errors

4. Create a namespace where we can run the job;

```
$ kubectl create namespace batch-job-example
```

5. switch to use that namespace by default:

```
$ kubectl config set-context --current --namespace=batch-job-example
```

6. Deploy rabbitmq to serve as a work queue

```
$ kubectl apply -f kubernetes/work-queue.yaml
```   

7. Create a secret to hold your username and password:
```
$ kubectl create secret generic aws-credential-secret \
  --from-literal=JOB_USER=my-user \
  --from-literal=JOB_PASS=my-pass 
```

8. if you're re-running, delete any old jobs running in the cluster;

```
kubectl delete job --all
```

9. run the loader

```
$ kubectl apply -f kubernetes/loader-job.yaml
```

10. check the loader worked by looking at the logs of the run;

```
$ k get pod -l job-name=load
NAME         READY   STATUS      RESTARTS   AGE
load-wg8g4   0/1     Completed   0          75s

$ kubectl logs load-wg8g4
connecting to work queue
connected to work queue
loading data: 0
loading data: 1
...
loading data: 98
loading data: 99
loaded data

```

11. Modify `./kubernetes/processor-job.yaml` to fill in any extra details like docker image or degree of parallelism.

12. now run the processor!

```
$ kubectl apply -f kubernetes/processor-job.yaml
```

13. see the status of the processor job itself;

```
$ kubectl describe job process
```

14. see the containers being spun up by the job

```
$ kubectl get pods -l job-name=process

NAME            READY   STATUS    RESTARTS   AGE
process-bb7bs   1/1     Running   0          23s
process-gr85n   1/1     Running   0          23s
process-mmqfv   1/1     Running   0          23s
process-q2rwv   1/1     Running   0          23s
process-rjk7w   1/1     Running   0          23s
```

15. see the logs of one pod in the batch;

```
$ kubectl logs process-bb7bs

credentials: my-user my-pass
connecting to work queue  work-queue 5672
connected to work queue
got id b'5'
acknowledged b'5'
 [x] Received b'5'
got id b'8'
acknowledged b'8'
 [x] Received b'8'
...
got id b'97'
acknowledged b'97'
 [x] Received b'97'
processed all work

```

Note how each processor instance does around 1/5th of the work because in processorjob.yaml, we've set parallelism to 5.
