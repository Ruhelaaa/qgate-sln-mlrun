"""
  TS603: Complex pipeline(s), mass operation
"""

from qgate_sln_mlrun.ts.tsbase import TSBase
from qgate_sln_mlrun.setup import Setup
import mlrun.feature_store as fstore
import mlrun
import pandas as pd
import glob
import os


class TS603(TSBase):

    def __init__(self, solution):
        super().__init__(solution, self.__class__.__name__)

    @property
    def desc(self) -> str:
        return "Complex pipeline(s), mass operation"

    @property
    def long_desc(self):
        return "Complex pipeline(s), mass operation"

    def exec(self):
        self._complex(f"*/class_complex_mass (event)", True)
        self._complex(f"*/complex_mass (event)", False)

    @TSBase.handler_testcase
    def _complex(self, testcase_name, class_call):

        echo_server=self._one_call_init(class_call)
        count=0
        try:
            for a in range(1, 200):
                a=a/100 if class_call else a/-100
                for b in range(1, 50):
                    b=b/10 if class_call else b/-10
                    count+=1
                    self._one_call(a, b, echo_server)
        finally:
            echo_server.wait_for_completion()
        self.testcase_detail(f"{count} calls")

    def _one_call_init(self, call_class):
        func = mlrun.code_to_function(f"ts603_fn",
                                      kind="serving",
                                      filename="./qgate_sln_mlrun/ts/ts06_pipeline/ts603_ext_code.py")
        graph_echo = func.set_topology("flow")
        if call_class:
            graph_echo.to(class_name="TS603Pipeline", full_event=True, name="step1") \
                    .to(class_name="TS603Pipeline", full_event=True, name="step2") \
                    .to(class_name="TS603Pipeline", full_event=True, name="step3") \
                    .to(class_name="TS603Pipeline", full_event=True, name="step4") \
                    .to(class_name="TS603Pipeline", full_event=True, name="step5").respond()
        else:
            graph_echo.to(handler="step1", full_event=True, name="step1") \
                .to(handler="step2", full_event=True, name="step2") \
                .to(handler="step3", full_event=True, name="step3") \
                .to(handler="step4", full_event=True, name="step4").respond()
        echo_server = func.to_mock_server(current_function="*")
        return echo_server

    def _one_call(self, a, b, echo_server):

        # tests
        result = echo_server.test("", {"a": a, "b": b})

        expected_value= (((a * b) + a + b) + min(a, b)) + pow(a, b)

        # value check
        if result['calc']!=expected_value:
            raise ValueError(f"Invalid calculation, expected value {expected_value}")

