import { SIM_TREE_V1 } from "../simulator_tree_v1.js";
import fs from "fs";

fs.writeFileSync(
  "../simulator_tree_v1.json",
  JSON.stringify(SIM_TREE_V1, null, 2),
  "utf-8"
);

console.log("Wrote simulator_tree_v1.json ✅");
