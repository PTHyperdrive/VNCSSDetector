use log::warn;
use serde::{Deserialize, Serialize};

use vncssdetector::Device;
use vncssdetector::analysis::analyzer::AnalyzerConfig;

use crate::error::VNCSSdetectorError;
use crate::notifications::NotificationType;

/// Running mode for VNCSSDetector daemon
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Default)]
#[serde(rename_all = "lowercase")]
pub enum RunningMode {
    #[default]
    Standalone,
    Node,
    Swarm,
}

/// Connection status for Node/Swarm modes
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Default)]
#[serde(rename_all = "lowercase")]
pub enum ConnectionStatus {
    #[default]
    Disconnected,
    Connecting,
    Connected,
    Error,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(default)]
pub struct Config {
    pub qmdl_store_path: String,
    pub port: u16,
    pub debug_mode: bool,
    pub device: Device,
    pub ui_level: u8,
    pub colorblind_mode: bool,
    pub key_input_mode: u8,
    pub ntfy_url: Option<String>,
    pub enabled_notifications: Vec<NotificationType>,
    pub analyzers: AnalyzerConfig,
    // Node/Swarm mode configuration
    pub running_mode: RunningMode,
    pub server_ip: Option<String>,
    pub api_key: Option<String>,
}

/// Runtime connection state (not persisted to config file)
#[derive(Debug, Clone, Serialize)]
pub struct NodeConnectionState {
    pub status: ConnectionStatus,
    pub server_ip: Option<String>,
    pub last_error: Option<String>,
    pub connected_at: Option<String>,
    pub is_heuristic_passed: bool,
}

impl Default for NodeConnectionState {
    fn default() -> Self {
        NodeConnectionState {
            status: ConnectionStatus::Disconnected,
            server_ip: None,
            last_error: None,
            connected_at: None,
            is_heuristic_passed: false,
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Config {
            qmdl_store_path: "/data/vncssdetector/qmdl".to_string(),
            port: 8080,
            debug_mode: false,
            device: Device::Orbic,
            ui_level: 1,
            colorblind_mode: false,
            key_input_mode: 0,
            analyzers: AnalyzerConfig::default(),
            ntfy_url: None,
            enabled_notifications: vec![NotificationType::Warning, NotificationType::LowBattery],
            // Default to standalone mode
            running_mode: RunningMode::Standalone,
            server_ip: None,
            api_key: None,
        }
    }
}

pub async fn parse_config<P>(path: P) -> Result<Config, VNCSSdetectorError>
where
    P: AsRef<std::path::Path>,
{
    if let Ok(config_file) = tokio::fs::read_to_string(&path).await {
        Ok(toml::from_str(&config_file).map_err(VNCSSdetectorError::ConfigFileParsingError)?)
    } else {
        warn!("unable to read config file, using default config");
        Ok(Config::default())
    }
}

pub struct Args {
    pub config_path: String,
}

pub fn parse_args() -> Args {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        println!("Usage: {} /path/to/config/file", args[0]);
        std::process::exit(1);
    }
    Args {
        config_path: args[1].clone(),
    }
}

