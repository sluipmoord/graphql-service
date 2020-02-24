import os
import yaml

STAGE = os.environ.get("STAGE")
REGION = os.environ.get("AWS_REGION", "eu-west-1")

try:
    secrets_file = "kms-secrets.{}.{}.yml".format(STAGE, REGION)
    with open(secrets_file, "r") as f:
        d = yaml.load(f, Loader=yaml.Loader)
        for k, v in d["secrets"].items():
            print("{}={}".format(k, v))
except:  # noqa: E722
    pass

env_file = "env.{}.yml".format(STAGE)
with open(env_file, "r") as f:
    d = yaml.load(f, Loader=yaml.Loader)
    for k, v in d.items():
        print("{}={}".format(k, v))
