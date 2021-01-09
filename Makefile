JOB_USER=my-user
JOB_PASS=my-password
TS=(shell date '%s')
PROCESSOR_IMAGE=stevecooperorg/work-queue-processor:latest
LOADER_IMAGE=stevecooperorg/work-queue-loader:latest

all: docker-build

docker-start-rabbit:
	docker run -d --hostname work-queue --name work-queue rabbitmq:3

docker-build:
	docker build loader -t $(LOADER_IMAGE)
	docker build processor -t $(PROCESSOR_IMAGE)

docker-run: docker-build
	docker run --rm --env JOB_USER=$(JOB_USER) --env JOB_PASS=$(JOB_PASS) $(PROCESSOR_IMAGE)

run:
	export JOB_USER=$(JOB_USER) && export JOB_PASS=$(JOB_PASS) && python src/main.py

docker-push: docker-build
	docker push $(PROCESSOR_IMAGE)
	docker push $(LOADER_IMAGE)

kube-delete-job:
	kubectl delete -f kubernetes/job.yaml

kube-run-job:
	kubectl apply -f kubernetes/job.yaml

kube-describe-job:
	kubectl describe job my-batch-job
	kubectl get pods -l job-name=my-batch-job

kube-rerun-job: docker-push
kube-rerun-job: kube-delete-job
kube-rerun-job: kube-run-job
kube-rerun-job:
	kubectl get job my-batch-job
	kubectl get pods -l job-name=my-batch-job

kube-delete-load:
	kubectl delete -f kubernetes/load.yaml

kube-run-load:
	kubectl apply -f kubernetes/load.yaml

kube-rerun-load: kube-delete-load
kube-rerun-load: kube-run-load