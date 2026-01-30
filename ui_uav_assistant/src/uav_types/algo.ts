export type Algo = "GA" | "ES";
export type Objective = "DISTANCE" | "ENERGY" | "WEATHER";
export interface AlgoSettings {
  algo: Algo;
  generations: number;
  populationSize: number;
  objectiveFunction: Objective;
  seed: number
  sigma0: number
  mutationProbability: number
  keepElitism: number
  kTournament: number
}
