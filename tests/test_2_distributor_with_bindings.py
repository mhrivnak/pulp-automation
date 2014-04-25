import pulp_test, json
from pulp_auto.repo import Repo
from pulp_auto.task import Task, TaskFailure
from pulp_test import (ConsumerAgentPulpTest, agent_test)
from pulp_auto.consumer import (Consumer, Binding)


class DistributorBindings(ConsumerAgentPulpTest):

    @agent_test(catching=True)
    def test_01_bind_distributor(self):
        with self.pulp.asserting(True):
            response = self.consumer.bind_distributor(self.pulp, self.repo.id, self.distributor.id)
            Task.wait_for_report(self.pulp, response)

    def test_03_update_distributor_config_via_repo_call(self):
        # https://bugzilla.redhat.com/show_bug.cgi?id=1078305
        # in this custom update you can update repo's info + importer/distributor
        response = self.repo.update(self.pulp, data={
                                                   "delta": {"display_name": "NewName"},
                                                   "importer_config": {"num_units": 6},
                                                   "distributor_configs": {
                                                   "yum_distributor": {"relative_url": "my_url"}
                                                                           }
                                                    }
                                   )
        # in this case when repo is bound to a consumer the response code will be 202)
        self.assertPulp(code=202)


    def test_02_delete_distributor(self):
        response = self.distributor.delete(self.pulp)
        Task.wait_for_report(self.pulp, response)

    def test_03_check_binding_removed(self):
        #https://bugzilla.redhat.com/show_bug.cgi?id=1081030
        # Consumers are not unbounded from distributor in case of distributor's removal
        consumer = Consumer.get(self.pulp, self.consumer.id, params={"bindings": True})
        self.assertTrue(consumer.data["bindings"] is None)
