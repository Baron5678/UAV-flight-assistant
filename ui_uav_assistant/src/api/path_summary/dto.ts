export interface PathSummaryRowResponseDto {
  generation: number;
  cost: number;
  total_distance_m: number;
}

export interface PathSummaryStatsResponseDto {
    best_cost: number;
    first_cost: number;
    min_cost: number;
    max_cost: number;
    avg_cost: number;
    min_total_distance_m: number;
    max_total_distance_m: number;
    avg_total_distance_m: number;
    improvement_abs: number;
    improvement_pct: number;
    improving_generations: number;
    last_improvement_generation: number | null;
    max_stagnation_generations: number;
}

export interface PathSummaryResponseDto {
  mission_id: number;
  paths: PathSummaryRowResponseDto[];
  stats: PathSummaryStatsResponseDto;
}

export interface PathSummaryPathParams {
  mission_id: number;
}
