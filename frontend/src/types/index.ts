// User types
export interface User {
  id: string;
  email: string;
  name: string;
  primary_sport: string;
}

export interface ThresholdValues {
  threshold_hr?: number;
  max_hr?: number;
  resting_hr?: number;
  threshold_power?: number;
  running_threshold_power?: number;
  critical_power?: number;
}

// Activity types
export interface ActivitySummary {
  id: string;
  sport: string;
  sub_sport?: string;
  name?: string;
  start_time: string;
  total_timer_time: number;
  total_distance?: number;
  avg_heart_rate?: number;
  avg_power?: number;
  normalized_power?: number;
  tss?: number;
  scaled_tss?: number;
  source: string;
}

export interface ActivityDetail extends ActivitySummary {
  end_time?: string;
  total_elapsed_time?: number;
  total_calories?: number;
  max_heart_rate?: number;
  max_power?: number;
  avg_cadence?: number;
  avg_speed?: number;
  max_speed?: number;
  total_ascent?: number;
  total_descent?: number;
  avg_stroke_rate?: number;
  intensity_factor?: number;
  description?: string;
  is_combined: boolean;
  has_records: boolean;
}

export interface RecordPoint {
  timestamp: string;
  heart_rate?: number;
  power?: number;
  cadence?: number;
  speed?: number;
  distance?: number;
  altitude?: number;
}

// Metrics types
export interface DailyMetrics {
  date: string;
  tss: number;
  scaled_tss: number;
  ctl: number;
  atl: number;
  tsb: number;
}

export interface PerformanceSnapshot {
  fitness: number;
  fatigue: number;
  form: number;
  total_tss_7d: number;
  total_tss_28d: number;
  total_duration_7d: number;
  total_distance_7d: number;
  ramp_rate_7d: number;
  ramp_rate_28d: number;
  ramp_rate_90d: number;
}

export interface WeeklySummary {
  week_start: string;
  total_tss: number;
  total_scaled_tss: number;
  total_duration: number;
  total_distance: number;
  activity_count: number;
  by_sport: Record<string, number>;
}

// Zone types
export interface Zone {
  zone_number: number;
  name: string;
  lower: number;
  upper: number;
}

export interface ZoneResult {
  method: string;
  activity: string;
  threshold_type: string;
  threshold_value: number;
  zones: Zone[];
}

export interface ZoneMethodInfo {
  method_id: string;
  name: string;
  zone_count: number;
  threshold_type: string;
  supports: string[];
}

// Workout types
export interface WorkoutStep {
  step_type: string;
  duration_type: string;
  duration_value?: number;
  target_type?: string;
  target_low?: number;
  target_high?: number;
  notes?: string;
}

export interface PlannedWorkout {
  id: string;
  scheduled_date: string;
  completed: boolean;
  activity_id?: string;
  name: string;
  description?: string;
  sport: string;
  estimated_duration?: number;
  estimated_tss?: number;
  steps: WorkoutStep[];
  pre_activity_comments?: string;
  post_activity_comments?: string;
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
