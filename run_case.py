import sys
import os
from core.dss_engine_agent import EngineAgent

def run_script_by_agent(dss_file_path):

    agent = EngineAgent(dss_file_path)
    agent.solve()

    v_node = agent.all_voltage()
    print(v_node)



if __name__ == "__main__":

    case1 = "dss_script/case1.dss"
    run_script_by_agent(case1)

    case2 = "dss_script/case2.dss"
    run_script_by_agent(case2)

    case3 = "dss_script/case3.dss"
    run_script_by_agent(case3)
    

    