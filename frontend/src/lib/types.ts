/**
 * TypeScript types matching backend Pydantic schemas.
 */

export interface IntentIR {
  app_name: string;
  features: string[];
  entities: string[];
  roles: string[];
  premium_features: string[];
  payment_provider: string | null;
  ambiguity_score: number;
  clarifications_needed: string[];
  assumptions: string[];
}

export interface EntityDesign {
  name: string;
  fields: string[];
  field_types: Record<string, string>;
  relations: string[];
}

export interface SystemDesignIR {
  app_name: string;
  entities: Record<string, EntityDesign>;
  flows: Record<string, string[]>;
  access_control_matrix: Record<string, string[]>;
  assumptions: string[];
}

export interface DBColumn {
  name: string;
  type: string;
  primary_key: boolean;
  nullable: boolean;
  unique: boolean;
  default: string | null;
  foreign_key: string | null;
}

export interface DBTable {
  name: string;
  entity: string;
  columns: DBColumn[];
  indexes: string[];
}

export interface DBSchema {
  tables: DBTable[];
}

export interface APIEndpoint {
  method: string;
  path: string;
  description: string;
  auth_required: boolean;
  roles: string[];
}

export interface APIResource {
  name: string;
  entity: string;
  base_path: string;
  endpoints: APIEndpoint[];
}

export interface APISchema {
  resources: APIResource[];
}

export interface UIComponent {
  type: string;
  props: Record<string, any>;
  data_source: string | null;
}

export interface UIPage {
  id: string;
  title: string;
  route: string;
  auth_required: boolean;
  roles: string[];
  components: UIComponent[];
}

export interface UISchema {
  pages: UIPage[];
}

export interface AuthSchema {
  strategy: string;
  token_expiry: string;
  refresh_token: boolean;
  password_storage: string;
  rate_limit_enabled: boolean;
  roles: string[];
  permissions: { role: string; permissions: string[] }[];
  guards: { name: string; required_roles: string[]; redirect: string }[];
}

export interface ExecutionCheck {
  name: string;
  passed: boolean;
  details: string;
  errors: string[];
}

export interface ExecutionReport {
  db_bootable: ExecutionCheck;
  api_complete: ExecutionCheck;
  ui_renderable: ExecutionCheck;
  auth_sane: ExecutionCheck;
  overall_pass: boolean;
}

export interface ValidatedAppConfig {
  metadata: { app_name: string; version: string; assumptions: string[] };
  domain: { entities: { name: string; fields: any[] }[] };
  auth: AuthSchema;
  db: DBSchema;
  api: APISchema;
  ui: UISchema;
  logic: { rules: any[] };
}

export interface CompileResponse {
  job_id: string;
  status: string;
  app_config: ValidatedAppConfig | null;
  execution_report: ExecutionReport | null;
  intent_ir: any | null;
  system_design_ir: any | null;
  validation_errors: any[];
  repair_log: any[];
  metrics: any;
  clarifications_needed: string[];
}
