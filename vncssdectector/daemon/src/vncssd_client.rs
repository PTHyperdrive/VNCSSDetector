//! VNCSSD Server WebSocket Client
//!
//! This module handles the connection between VNCSSDetector nodes and the
//! VNCSSD central server for real-time alert reporting and status updates.

use futures::{SinkExt, StreamExt};
use log::{debug, error, info, warn};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::{RwLock, mpsc};
use tokio::time::{Duration, interval};
use tokio_tungstenite::{connect_async, tungstenite::Message};
use url::Url;

use crate::config::{ConnectionStatus, NodeConnectionState, RunningMode};

/// Message types for VNCSSDetector ↔ Server protocol
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum MessageType {
    // Client → Server
    Register,
    Heartbeat,
    Telemetry,
    Event,
    Alert,
    // Server → Client
    Connected,
    Registered,
    HeartbeatAck,
    TelemetryAck,
    EventAck,
    AlertAck,
    Command,
    Error,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeMessage {
    pub msg_type: String,
    pub msg_id: String,
    pub timestamp: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub node_id: Option<String>,
    pub payload: serde_json::Value,
}

impl NodeMessage {
    pub fn new(msg_type: &str, payload: serde_json::Value) -> Self {
        NodeMessage {
            msg_type: msg_type.to_string(),
            msg_id: format!("{}-{}", chrono::Utc::now().timestamp_millis(), rand_id()),
            timestamp: chrono::Utc::now().to_rfc3339(),
            node_id: None,
            payload,
        }
    }
}

fn rand_id() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .subsec_nanos();
    format!("{:x}", nanos)
}

/// Alert data to send to VNCSSD server
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertData {
    pub alert_type: String,
    pub alert_message: String,
    pub data: serde_json::Value,
}

/// VNCSSD Server Client
pub struct VncssdClient {
    server_url: String,
    api_key: String,
    connection_state: Arc<RwLock<NodeConnectionState>>,
    alert_sender: mpsc::Sender<AlertData>,
    alert_receiver: Option<mpsc::Receiver<AlertData>>,
}

impl VncssdClient {
    pub fn new(
        server_ip: String,
        api_key: String,
        connection_state: Arc<RwLock<NodeConnectionState>>,
    ) -> Self {
        let (alert_sender, alert_receiver) = mpsc::channel(100);

        // Construct WebSocket URL
        let server_url = if server_ip.starts_with("ws://") || server_ip.starts_with("wss://") {
            format!("{}/nodes", server_ip)
        } else {
            format!("ws://{}/nodes", server_ip)
        };

        VncssdClient {
            server_url,
            api_key,
            connection_state,
            alert_sender,
            alert_receiver: Some(alert_receiver),
        }
    }

    /// Get a sender to queue alerts
    pub fn get_alert_sender(&self) -> mpsc::Sender<AlertData> {
        self.alert_sender.clone()
    }

    /// Start the WebSocket connection loop
    pub async fn run(mut self) {
        let mut alert_receiver = self.alert_receiver.take().unwrap();

        loop {
            // Update status to connecting
            {
                let mut state = self.connection_state.write().await;
                state.status = ConnectionStatus::Connecting;
                state.server_ip = Some(self.server_url.clone());
            }

            match self.connect_and_run(&mut alert_receiver).await {
                Ok(_) => {
                    info!("VNCSSD connection closed normally");
                }
                Err(e) => {
                    error!("VNCSSD connection error: {}", e);
                    let mut state = self.connection_state.write().await;
                    state.status = ConnectionStatus::Error;
                    state.last_error = Some(e.to_string());
                }
            }

            // Update status to disconnected
            {
                let mut state = self.connection_state.write().await;
                state.status = ConnectionStatus::Disconnected;
            }

            // Wait before reconnecting
            tokio::time::sleep(Duration::from_secs(5)).await;
            info!("Attempting to reconnect to VNCSSD server...");
        }
    }

    async fn connect_and_run(
        &self,
        alert_receiver: &mut mpsc::Receiver<AlertData>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let url = Url::parse(&self.server_url)?;

        info!("Connecting to VNCSSD server: {}", self.server_url);

        let (ws_stream, _) = connect_async(url).await?;
        let (mut write, mut read) = ws_stream.split();

        // Send authentication
        let auth_msg = NodeMessage::new(
            "REGISTER",
            serde_json::json!({
                "api_key": self.api_key,
                "hostname": hostname::get()
                    .map(|h| h.to_string_lossy().to_string())
                    .unwrap_or_else(|_| "unknown".to_string()),
                "capabilities": ["imsi_detection", "signal_analysis"],
                "version": env!("CARGO_PKG_VERSION"),
            }),
        );

        write
            .send(Message::Text(serde_json::to_string(&auth_msg)?))
            .await?;

        // Update status to connected
        {
            let mut state = self.connection_state.write().await;
            state.status = ConnectionStatus::Connected;
            state.connected_at = Some(chrono::Utc::now().to_rfc3339());
            state.last_error = None;
        }

        info!("Connected to VNCSSD server");

        // Heartbeat interval
        let mut heartbeat_interval = interval(Duration::from_secs(30));

        loop {
            tokio::select! {
                // Handle incoming messages
                Some(msg) = read.next() => {
                    match msg {
                        Ok(Message::Text(text)) => {
                            if let Ok(node_msg) = serde_json::from_str::<NodeMessage>(&text) {
                                self.handle_server_message(&node_msg).await;
                            }
                        }
                        Ok(Message::Close(_)) => {
                            info!("Server closed connection");
                            break;
                        }
                        Err(e) => {
                            error!("WebSocket error: {}", e);
                            break;
                        }
                        _ => {}
                    }
                }

                // Send queued alerts
                Some(alert) = alert_receiver.recv() => {
                    let alert_msg = NodeMessage::new("ALERT", serde_json::json!({
                        "alert_type": alert.alert_type,
                        "alert_message": alert.alert_message,
                        "data": alert.data,
                    }));

                    if let Err(e) = write.send(Message::Text(serde_json::to_string(&alert_msg)?)).await {
                        error!("Failed to send alert: {}", e);
                        break;
                    }
                    debug!("Sent alert: {}", alert.alert_type);
                }

                // Send heartbeat
                _ = heartbeat_interval.tick() => {
                    let heartbeat = NodeMessage::new("HEARTBEAT", serde_json::json!({
                        "status": "online",
                        "timestamp": chrono::Utc::now().to_rfc3339(),
                    }));

                    if let Err(e) = write.send(Message::Text(serde_json::to_string(&heartbeat)?)).await {
                        error!("Failed to send heartbeat: {}", e);
                        break;
                    }
                    debug!("Sent heartbeat");
                }
            }
        }

        Ok(())
    }

    async fn handle_server_message(&self, msg: &NodeMessage) {
        match msg.msg_type.as_str() {
            "REGISTERED" => {
                info!("Successfully registered with VNCSSD server");
            }
            "HEARTBEAT_ACK" => {
                debug!("Heartbeat acknowledged");
            }
            "ALERT_ACK" => {
                debug!("Alert acknowledged: {}", msg.msg_id);
            }
            "COMMAND" => {
                info!("Received command from server: {:?}", msg.payload);
                // TODO: Handle commands from server
            }
            "ERROR" => {
                let code = msg
                    .payload
                    .get("code")
                    .and_then(|v| v.as_str())
                    .unwrap_or("UNKNOWN");
                let message = msg
                    .payload
                    .get("message")
                    .and_then(|v| v.as_str())
                    .unwrap_or("Unknown error");
                error!("Server error: {} - {}", code, message);
            }
            _ => {
                debug!("Unknown message type: {}", msg.msg_type);
            }
        }
    }
}

/// Start the VNCSSD client if in Node or Swarm mode
pub async fn start_vncssd_client(
    running_mode: RunningMode,
    server_ip: Option<String>,
    api_key: Option<String>,
    connection_state: Arc<RwLock<NodeConnectionState>>,
) -> Option<mpsc::Sender<AlertData>> {
    // Only connect if in Node or Swarm mode with valid config
    if running_mode == RunningMode::Standalone {
        info!("Running in Standalone mode - not connecting to VNCSSD server");
        return None;
    }

    let server_ip = match server_ip {
        Some(ip) if !ip.is_empty() => ip,
        _ => {
            warn!("No server IP configured for Node/Swarm mode");
            return None;
        }
    };

    let api_key = match api_key {
        Some(key) if !key.is_empty() => key,
        _ => {
            warn!("No API key configured for Node/Swarm mode");
            return None;
        }
    };

    let client = VncssdClient::new(server_ip, api_key, connection_state);
    let alert_sender = client.get_alert_sender();

    // Spawn the client in background
    tokio::spawn(async move {
        client.run().await;
    });

    Some(alert_sender)
}
