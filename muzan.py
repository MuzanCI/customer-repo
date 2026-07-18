# muzan.star — MuzanCI pipeline configuration example.
#
# The primitives secret(), step(), job(), and pipeline() are provided by the
# interpreter as Rust StarlarkValue globals.  This file shows how to compose
# them into a real CI workflow.

# ------------------------------------------------------------------------------
# Reusable step helpers (Starlark-level wrappers around the step() primitive).
# ------------------------------------------------------------------------------


def checkout(clone_url, branch):
    return Step(
        name="checkout {} {}".format(clone_url, branch),
        command="git clone --branch {} {} .".format(branch, clone_url),
    )


def upload(source, destination, secrets=[]):
    return Step(
        name="upload {} {}".format(source, destination),
        command="aws s3 upload {} {}".format(source, destination),
        secrets=secrets,
    )


def download(source, destination, secrets=[]):
    return Step(
        name="download {} {}".format(source, destination),
        command="aws s3 download {} {}".format(source, destination),
        secrets=secrets,
    )


def attest(glob, oidc_issuer, secrets=[]):
    command = "attest {} {}".format(glob, oidc_issuer)
    return Step(
        name=command,
        command=command,
        secrets=secrets,
    )


# ------------------------------------------------------------------------------
# Pipeline definition
# ------------------------------------------------------------------------------

aws_secret = Secret(
    name="aws_secret",
    key="AWS_SECRET_ACCESS_KEY",
)

build_job = Job(
    name="build_job",
    steps=[
        # checkout(
        #     clone_url=GIT_CLONE_URL,
        #     branch=GIT_BRANCH,
        # ),
        # Step(
        #     name="build",
        #     command="cargo build --release",
        # ),
        # attest(
        #     glob="target/release/my_binary",
        #     oidc_issuer="https://oidc.example.com",
        # ),
        # upload(
        #     source="target/release/my_binary",
        #     destination="s3://my-bucket/{}/my_binary".format(GIT_COMMIT),
        #     secrets=[aws_secret],
        # ),
        Step(
            name="build",
            command="echo 'build_job executing...'",
        )
    ],
)

test_job = Job(
    name="test_job",
    needs=[
        build_job,  # TODO: evaluate to Need(job_id, Completed)
    ],
    steps=[
        # download(
        #     source="s3://my-bucket/{}/my_binary".format(GIT_COMMIT),
        #     destination="./my_binary",
        # ),
        # Step(
        #     name="test",
        #     command="./my_binary --test --output results.json",
        # ),
        # attest(
        #     glob="results.json",
        #     oidc_issuer="https://oidc.example.com",
        # ),
        Step(
            name="test",
            command="echo 'test_job executing...'",
        )
    ],
)

clean_up_job = Job(
    name="clean_up_job",
    needs=[
        test_job.failed,
    ],
    steps=[
        # Step(
        #     name="clean up",
        #     command="rm -rf target/release/my_binary",
        # ),
        Step(
            name="clean up",
            command="echo 'clean_up_job executing...'",
        ),
    ],
)

no_name_job = Job(
    steps=[],
)

no_name2_job = Job(
    steps=[],
)

load("external.py", "external_job")

# pipeline() is called for its side effect: it registers the pipeline in the
# interpreter's collector.  It does not need to be assigned to a variable.
for arch in ["x86_64", "arm64"]:
    Pipeline(
        name=f"release_{arch}",
        when=[
            Push(),
        ],
        needs=[test_job, external_job],
    )
