use crate::limits::{enforce_limits, LicenseTier, LimitPolicy};
use crate::models::fers::fers::FERS;
use crate::models::settings::analysissettings::AnalysisOrder;
use nalgebra::DMatrix;
use serde_json;
use std::fs;
use std::io;
use std::path::Path;

/// Central pipeline that both the binary and Python call.
/// The caller controls bounds by choosing the LimitPolicy (Free or Premium).
pub fn run_pipeline_from_json_with_policy(
    json_data: &str,
    policy: LimitPolicy,
) -> Result<String, String> {
    let mut fers: FERS =
        serde_json::from_str(json_data).map_err(|error| format!("Bad JSON input: {}", error))?;

    // Enforce license-based limits before any solving.
    enforce_limits(&fers, &policy)?;

    // Helpful for debugging path differences:
    log::info!(
        "License tier = {:?}, member_limit = {}",
        policy.license_tier,
        policy.allowed_max_members()
    );

    let options = &fers.settings.analysis_options;
    log::info!(
        "Analysis configuration → order={:?}, rigid_strategy={:?}, solve_loadcases={}, max_iterations={}, tolerance={}",
        options.order,
        options.rigid_strategy,
        options.solve_loadcases,
        options.max_iterations.unwrap_or(20),
        options.tolerance
    );
    log::info!(
        "Model summary → member_sets={}, members_total={}, load_cases={}, load_combinations={}",
        fers.member_sets.len(),
        fers.get_member_count(),
        fers.load_cases.len(),
        fers.load_combinations.len()
    );

    let is_second_order: bool = matches!(options.order, AnalysisOrder::Nonlinear);
    let tolerance: f64 = options.tolerance;
    let maximum_iterations: usize = options.max_iterations.unwrap_or(20) as usize;

    let load_case_ids: Vec<u32> = fers.load_cases.iter().map(|lc| lc.id).collect();
    let load_combination_ids: Vec<u32> = fers.load_combinations.iter().map(|c| c.id).collect();

    if options.solve_loadcases {
        for lc_id in load_case_ids {
            if is_second_order {
                log::info!(
                    "Solving load case {} with second-order (Newton–Raphson), tolerance={}, max_iterations={}",
                    lc_id,
                    tolerance,
                    maximum_iterations
                );
                fers.solve_for_load_case_second_order(lc_id, maximum_iterations, tolerance)
                    .map_err(|error| format!("LC {} second-order error: {}", lc_id, error))?;
            } else {
                log::info!("Solving load case {} with first-order (linear).", lc_id);
                fers.solve_for_load_case(lc_id)
                    .map_err(|error| format!("LC {} linear error: {}", lc_id, error))?;
            }
        }
    } else {
        log::info!("Skipping load cases because 'solve_loadcases' is false.");
    }

    for combo_id in load_combination_ids {
        if is_second_order {
            log::info!(
                "Solving load combination {} with second-order (Newton–Raphson), tolerance={}, max_iterations={}",
                combo_id,
                tolerance,
                maximum_iterations
            );
            fers.solve_for_load_combination_second_order(combo_id, maximum_iterations, tolerance)
                .map_err(|error| format!("Combo {} second-order error: {}", combo_id, error))?;
        } else {
            log::info!(
                "Solving load combination {} with first-order (linear).",
                combo_id
            );
            fers.solve_for_load_combination(combo_id)
                .map_err(|error| format!("Combo {} linear error: {}", combo_id, error))?;
        }
    }

    if let Some(bundle) = fers.results.take() {
        serde_json::to_string(&bundle)
            .map_err(|error| format!("Failed to serialize ResultsBundle: {}", error))
    } else {
        Err("No results were generated".to_string())
    }
}

/// Bounded entry for library/Python: uses Free tier limits.
pub fn calculate_from_json_internal(json_data: &str) -> Result<String, String> {
    run_pipeline_from_json_with_policy(json_data, LimitPolicy::free())
}

/// Bounded entry for library/Python: reads file and applies Free tier limits.
pub fn calculate_from_file_internal(path: &str) -> Result<String, String> {
    let file_content = fs::read_to_string(path)
        .map_err(|error| format!("Failed to read JSON file '{}': {}", path, error))?;
    calculate_from_json_internal(&file_content)
}

/// Premium entry for the binary: uses Premium tier limits.
pub fn calculate_from_json_internal_with_tier(
    json_data: &str,
    license_tier: LicenseTier,
) -> Result<String, String> {
    let policy = LimitPolicy::with_tier(license_tier);
    run_pipeline_from_json_with_policy(json_data, policy)
}

/// Premium entry for the binary: reads file and applies Premium tier limits.
pub fn calculate_from_file_internal_with_tier(
    path: &str,
    license_tier: LicenseTier,
) -> Result<String, String> {
    let file_content = fs::read_to_string(path)
        .map_err(|error| format!("Failed to read JSON file '{}': {}", path, error))?;
    calculate_from_json_internal_with_tier(&file_content, license_tier)
}

/// Optional pretty-printer for vectors (kept intact).
#[allow(dead_code)]
fn print_readable_vector(vector: &DMatrix<f64>, label: &str) {
    let dof_labels = ["UX", "UY", "UZ", "RX", "RY", "RZ"];
    println!("{}:", label);

    let num_nodes = vector.nrows() / 6;
    for node_index in 0..num_nodes {
        println!("  Node {}:", node_index + 1);
        for dof_index in 0..6 {
            let value = vector[(node_index * 6 + dof_index, 0)];
            println!("    {:<3}: {:10.4}", dof_labels[dof_index], value);
        }
    }
}

pub fn load_fers_from_file<P: AsRef<Path>>(path: P) -> Result<FERS, io::Error> {
    let s = fs::read_to_string(path)?;
    let fers: FERS = serde_json::from_str(&s)
        .map_err(|error| io::Error::new(io::ErrorKind::InvalidData, error))?;
    Ok(fers)
}
