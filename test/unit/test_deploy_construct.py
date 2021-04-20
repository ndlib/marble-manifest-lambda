import unittest

from aws_cdk import core

from deploy.deploy_constructs import DeployConstruct


class TestDeployConstruct(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = core.Stack(self.app, "TestStack")

    # def test_num_buckets(self):
    #     num_buckets = 1
    #     hello = DeployConstruct(self.stack, "Test1", num_buckets)
    #     assert len(hello.buckets) == num_buckets
