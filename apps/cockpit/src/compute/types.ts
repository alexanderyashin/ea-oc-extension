export type ShockType = "infra_capacity_drop" | "node_failure_rate";
export type ShockScope = "selected" | "all_systems";
export type ShockIntensity = 0.1 | 0.3 | 0.5;

export type SimConfig = {
  shockType: ShockType;
  scope: ShockScope;
  intensity: ShockIntensity;
};

export type NodeState = "OK" | "WARN" | "RED" | "STOP";

export type LedgerEvent =
  | {
      type: "threshold_crossed";
      step: number;
      nodeId: string;
      nodeLabel: string;
      threshold: NodeState; // the new state reached
      prev: NodeState;
      scorePrev: number;
      scoreNext: number;
    }
  | {
      type: "info";
      step: number;
      message: string;
    }
  | {
      type: "global_stop";
      step: number;
      reason: string;
    };

export type SimResult = {
  nodeStates: Record<string, NodeState>;
  nodeScores: Record<string, number>;
  ledger: LedgerEvent[];
  stop: boolean;
};
