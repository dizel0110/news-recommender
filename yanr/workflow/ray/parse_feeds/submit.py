from ray.job_submission import JobSubmissionClient
# from ray.job_submission import JobStatus
import asyncio

# If using a remote cluster, replace 127.0.0.1 with the head node's IP address.
client = JobSubmissionClient("http://127.0.0.1:8265")

# for x in client.list_jobs():
#     client.stop_job(x)

job_id = client.submit_job(
    entrypoint="python main.py config.yaml",
    runtime_env={"working_dir": "."}
)


async def log():
    async for lines in client.tail_job_logs(job_id):
        print(lines, end="")


asyncio.run(log())
