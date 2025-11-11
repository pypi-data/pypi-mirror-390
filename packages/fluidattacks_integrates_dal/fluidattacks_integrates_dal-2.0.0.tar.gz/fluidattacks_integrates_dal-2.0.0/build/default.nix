{ nixpkgs, builders, scripts, src, }: {
  inherit src;
  root_path = "observes/common/integrates-dal";
  module_name = "fluidattacks_integrates_dal";
  pypi_token_var = "INTEGRATES_DAL_TOKEN";
  override = b: b;
}
