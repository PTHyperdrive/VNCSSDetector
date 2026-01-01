//! DIAG device support for newer Qualcomm chipsets (Snapdragon 855+)
//!
//! This module provides extended IOCTL parameter structures and initialization
//! routines for modern Qualcomm SoCs that use updated diag driver interfaces.
//!
//! Supported chipsets:
//! - Snapdragon 855 (SM8150)
//! - Snapdragon 865 (SM8250)
//! - Snapdragon 888 (SM8350)
//! - And other modern Qualcomm SoCs with similar diag drivers

use crate::diag::{
    CRC_CCITT, DataType, DiagParsingError, LogConfigRequest, LogConfigResponse, Message,
    MessagesContainer, Request, RequestContainer, ResponsePayload, build_log_mask_request,
};
use crate::hdlc::hdlc_encapsulate;
use crate::Device;
use crate::diag_device::{DiagDeviceError, DiagResult, LOG_CODES_FOR_RAW_PACKET_LOGGING};

use deku::prelude::*;
use futures::TryStream;
use log::{debug, error, info, warn};
use std::io::ErrorKind;
use std::os::fd::AsRawFd;
use std::time::Duration;
use tokio::fs::File;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::time::sleep;

const BUFFER_LEN: usize = 1024 * 1024 * 10;
const MEMORY_DEVICE_MODE: u32 = 2;

// IOCTL constants for aarch64/musl
#[cfg(target_env = "musl")]
const DIAG_IOCTL_REMOTE_DEV: i32 = 32;
#[cfg(all(not(target_env = "musl"), target_arch = "aarch64"))]
const DIAG_IOCTL_REMOTE_DEV: u64 = 32;

#[cfg(target_env = "musl")]
const DIAG_IOCTL_SWITCH_LOGGING: i32 = 7;
#[cfg(all(not(target_env = "musl"), target_arch = "aarch64"))]
const DIAG_IOCTL_SWITCH_LOGGING: u64 = 7;

// V1 structure (legacy devices)
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct DiagLoggingModeParam {
    req_mode: u32,
    peripheral_mask: u32,
    mode_param: u8,
}

// V2 Extended structure for newer Qualcomm chips (Snapdragon 855+)
// See: https://android.googlesource.com/kernel/msm.git/+/refs/heads/android-msm-coral-4.14-android11/drivers/char/diag/diagchar.h
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct DiagLoggingModeParamV2 {
    req_mode: u32,
    peripheral_mask: u32,
    pd_mask: u32,
    mode_param: u32,
    diag_id: u8,
    pd_val: u8,
    peripheral: u8,
    reserved: u8,
}

// V3 structure for even newer devices (Android 12+)
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct DiagLoggingModeParamV3 {
    req_mode: u32,
    peripheral_mask: u32,
    pd_mask: u32,
    mode_param: u32,
    diag_id: u8,
    pd_val: u8,
    peripheral: u8,
    device_mask: u8,
    reserved: [u8; 4],
}

/// Extended DIAG device for newer Qualcomm chipsets
pub struct NewDiagDevice {
    file: File,
    read_buf: Vec<u8>,
    use_mdm: i32,
}

impl NewDiagDevice {
    /// Create a new DIAG device with extended support for newer Qualcomm chips
    pub async fn new(configured_device: &Device) -> DiagResult<Self> {
        Self::new_with_retries(Duration::from_secs(30), configured_device).await
    }

    pub async fn new_with_retries(
        max_duration: Duration,
        configured_device: &Device,
    ) -> DiagResult<Self> {
        let start_time = std::time::Instant::now();
        let max_delay = Duration::from_secs(5);

        let mut delay = Duration::from_millis(100);
        let mut num_retries = 0;

        loop {
            match Self::try_new(configured_device).await {
                Ok(device) => {
                    info!("NewDiagDevice initialization succeeded after {num_retries} retries");
                    return Ok(device);
                }
                Err(e) => {
                    num_retries += 1;
                    if start_time.elapsed() >= max_duration {
                        error!("Failed to initialize NewDiagDevice after {max_duration:?}: {e}");
                        return Err(e);
                    }

                    info!(
                        "NewDiagDevice initialization failed {num_retries} times, retrying in {delay:?}: {e}"
                    );
                    sleep(delay).await;

                    // Exponential backoff
                    delay = std::cmp::min(delay * 2, max_delay);
                }
            }
        }
    }

    async fn try_new(configured_device: &Device) -> DiagResult<Self> {
        let diag_file = File::options()
            .read(true)
            .write(true)
            .open("/dev/diag")
            .await
            .map_err(DiagDeviceError::OpenDiagDeviceError)?;
        let fd = diag_file.as_raw_fd();

        enable_frame_readwrite_extended(fd, MEMORY_DEVICE_MODE, configured_device)?;
        let use_mdm = determine_use_mdm_extended(fd)?;

        Ok(NewDiagDevice {
            read_buf: vec![0; BUFFER_LEN],
            file: diag_file,
            use_mdm,
        })
    }

    pub fn as_stream(
        &mut self,
    ) -> impl TryStream<Ok = MessagesContainer, Error = DiagDeviceError> + '_ {
        futures::stream::try_unfold(self, |dev| async {
            let container = dev.get_next_messages_container().await?;
            Ok(Some((container, dev)))
        })
    }

    async fn get_next_messages_container(&mut self) -> Result<MessagesContainer, DiagDeviceError> {
        let mut bytes_read = 0;
        while bytes_read <= 8 {
            bytes_read = self
                .file
                .read(&mut self.read_buf)
                .await
                .map_err(DiagDeviceError::DeviceReadFailed)?;
        }

        debug!(
            "Parsing messages container size = {:?} [{:?}]",
            bytes_read,
            &self.read_buf[0..bytes_read]
        );

        match MessagesContainer::from_bytes((&self.read_buf[0..bytes_read], 0)) {
            Ok((_, container)) => Ok(container),
            Err(err) => Err(DiagDeviceError::ParseMessagesContainerError(err)),
        }
    }

    async fn write_request(&mut self, req: &Request) -> DiagResult<()> {
        let req_bytes = &req.to_bytes().expect("Failed to serialize Request");
        let buf = RequestContainer {
            data_type: DataType::UserSpace,
            use_mdm: self.use_mdm > 0,
            mdm_field: -1,
            hdlc_encapsulated_request: hdlc_encapsulate(req_bytes, &CRC_CCITT),
        }
        .to_bytes()
        .expect("Failed to serialize RequestContainer");
        if let Err(err) = self.file.write(&buf).await {
            if err.kind() != ErrorKind::WriteZero {
                return Err(DiagDeviceError::DeviceWriteFailed(err));
            }
        }
        if let Err(err) = self.file.flush().await
            && err.kind() != ErrorKind::WriteZero
        {
            return Err(DiagDeviceError::DeviceWriteFailed(err));
        }
        Ok(())
    }

    async fn read_response(&mut self) -> DiagResult<Vec<Result<Message, DiagParsingError>>> {
        loop {
            let container = self.get_next_messages_container().await?;
            if container.data_type != DataType::UserSpace {
                continue;
            }
            return Ok(container.into_messages());
        }
    }

    async fn retrieve_id_ranges(&mut self) -> DiagResult<[u32; 16]> {
        let req = Request::LogConfig(LogConfigRequest::RetrieveIdRanges);
        self.write_request(&req).await?;

        for msg in self.read_response().await? {
            match msg {
                Ok(Message::Log { .. }) => info!("skipping log response..."),
                Ok(Message::Response {
                    payload, status, ..
                }) => match payload {
                    ResponsePayload::LogConfig(LogConfigResponse::RetrieveIdRanges {
                        log_mask_sizes,
                    }) => {
                        if status != 0 {
                            return Err(DiagDeviceError::RequestFailed(status, req));
                        }
                        return Ok(log_mask_sizes);
                    }
                    _ => info!("skipping non-LogConfigResponse response..."),
                },
                Err(e) => error!("error parsing message: {e:?}"),
            }
        }

        Err(DiagDeviceError::NoResponse(req))
    }

    async fn set_log_mask(&mut self, log_type: u32, log_mask_bitsize: u32) -> DiagResult<()> {
        let req = build_log_mask_request(
            log_type,
            log_mask_bitsize,
            &LOG_CODES_FOR_RAW_PACKET_LOGGING,
        );
        self.write_request(&req).await?;

        for msg in self.read_response().await? {
            match msg {
                Ok(Message::Log { .. }) => info!("skipping log response..."),
                Ok(Message::Response {
                    payload, status, ..
                }) => {
                    if let ResponsePayload::LogConfig(LogConfigResponse::SetMask) = payload {
                        if status != 0 {
                            return Err(DiagDeviceError::RequestFailed(status, req));
                        }
                        return Ok(());
                    }
                }
                Err(e) => error!("error parsing message: {e:?}"),
            }
        }

        Err(DiagDeviceError::NoResponse(req))
    }

    pub async fn config_logs(&mut self) -> DiagResult<()> {
        info!("retrieving diag logging capabilities...");
        let log_mask_sizes = self.retrieve_id_ranges().await?;

        for (log_type, &log_mask_bitsize) in log_mask_sizes.iter().enumerate() {
            if log_mask_bitsize > 0 {
                self.set_log_mask(log_type as u32, log_mask_bitsize).await?;
                info!("enabled logging for log type {log_type}");
            }
        }

        Ok(())
    }
}

const DIAG_IOCTL_LSM_DEINIT: i32 = 9;

/// Extended enable_frame_readwrite with support for newer Qualcomm chips
fn enable_frame_readwrite_extended(fd: i32, mode: u32, configured_device: &Device) -> DiagResult<()> {
    unsafe {
        // Try DEINIT first to clear any stale state
        info!("Attempting DIAG_IOCTL_LSM_DEINIT...");
        if libc::ioctl(fd, DIAG_IOCTL_LSM_DEINIT, 0, 0, 0, 0) >= 0 {
             info!("DIAG_IOCTL_LSM_DEINIT successful");
        } else {
             let err = std::io::Error::last_os_error();
             info!("DIAG_IOCTL_LSM_DEINIT failed (ignoring): {err}");
        }

        // Try setting to NO_LOGGING_MODE (0) first to reset
        info!("Attempting to reset to NO_LOGGING_MODE (0)...");
        if libc::ioctl(fd, DIAG_IOCTL_SWITCH_LOGGING, 0, 0, 0, 0) >= 0 {
            info!("Reset to NO_LOGGING_MODE successful");
        }

        // First try the simple integer mode (works on older devices)
        if libc::ioctl(fd, DIAG_IOCTL_SWITCH_LOGGING, mode, 0, 0, 0) >= 0 {
            info!("DIAG initialized with simple mode {mode}");
            return Ok(());
        } else {
            let err = std::io::Error::last_os_error();
             info!("Simple mode {mode} failed: {err}");
        }

        // Try V3 structure (newest devices, Android 12+)
        info!("Trying V3 DIAG structure for newer devices...");
        for peripheral_mask in [0xFFFFFFFF_u32, 0xFF_u32, 0x0_u32, 0x3_u32] {
            for mode_param in [1_u32, 0_u32, 2_u32] {
                let mut params = DiagLoggingModeParamV3 {
                    req_mode: mode,
                    peripheral_mask,
                    pd_mask: 0,
                    mode_param,
                    diag_id: 0,
                    pd_val: 0,
                    peripheral: 0,
                    device_mask: 0,
                    reserved: [0; 4],
                };
                if libc::ioctl(
                    fd,
                    DIAG_IOCTL_SWITCH_LOGGING,
                    &mut params as *mut DiagLoggingModeParamV3,
                    std::mem::size_of::<DiagLoggingModeParamV3>(),
                    0,
                    0,
                    0,
                    0,
                ) >= 0 {
                    info!("DIAG initialized with V3 structure (peripheral_mask={peripheral_mask:#x}, mode_param={mode_param})");
                    return Ok(());
                } else {
                    let err = std::io::Error::last_os_error();
                    info!("V3 structure failed (mask={peripheral_mask:#x}, param={mode_param}): {err}");
                }
            }
        }

        // Try V2 extended structure (Snapdragon 855+)
        info!("Trying V2 DIAG structure for Snapdragon 855+...");
        for peripheral_mask in [0xFFFFFFFF_u32, 0xFF_u32, 0x0_u32, 0x3_u32] {
            // Try both default mode (2) and USB mode (1) if default fails
            for try_mode in [mode, 1] { 
                for mode_param in [1_u32, 0_u32, 2_u32] {
                    let mut params = DiagLoggingModeParamV2 {
                        req_mode: try_mode,
                        peripheral_mask,
                        pd_mask: 0,
                        mode_param,
                        diag_id: 0,
                        pd_val: 0,
                        peripheral: 0,
                        reserved: 0,
                    };
                    if libc::ioctl(
                        fd,
                        DIAG_IOCTL_SWITCH_LOGGING,
                        &mut params as *mut DiagLoggingModeParamV2,
                        std::mem::size_of::<DiagLoggingModeParamV2>(),
                        0,
                        0,
                        0,
                        0,
                    ) >= 0 {
                        info!("DIAG initialized with V2 structure (mode={try_mode}, peripheral_mask={peripheral_mask:#x}, mode_param={mode_param})");
                        return Ok(()); // We accept USB mode if Memory mode fails
                    } else {
                        let err = std::io::Error::last_os_error();
                        info!("V2 structure failed (mode={try_mode}, mask={peripheral_mask:#x}, param={mode_param}): {err}");
                    }
                }
            }
        }

        // Fall back to V1 structure (legacy devices)
        info!("Falling back to V1 DIAG structure...");
        let mut try_params = vec![
            DiagLoggingModeParam {
                req_mode: mode,
                peripheral_mask: u32::MAX,
                mode_param: 0,
            },
            DiagLoggingModeParam {
                req_mode: mode,
                peripheral_mask: 0,
                mode_param: 1,
            },
        ];

        if configured_device == &Device::Tplink {
            // tplink M7350 HW revision 3-8 need this mode first
            try_params.reverse();
        }

        for params in &try_params {
            let mut params = *params;
            if libc::ioctl(
                fd,
                DIAG_IOCTL_SWITCH_LOGGING,
                &mut params as *mut DiagLoggingModeParam,
                std::mem::size_of::<DiagLoggingModeParam>(),
                0,
                0,
                0,
                0,
            ) >= 0 {
                info!("DIAG initialized with V1 structure");
                return Ok(());
            }
        }

        let msg = "DIAG_IOCTL_SWITCH_LOGGING failed with all parameter variants".to_string();
        Err(DiagDeviceError::InitializationFailed(msg))
    }
}

fn determine_use_mdm_extended(fd: i32) -> DiagResult<i32> {
    let use_mdm: i32 = 0;
    unsafe {
        if libc::ioctl(fd, DIAG_IOCTL_REMOTE_DEV, &use_mdm as *const i32) < 0 {
            // On newer devices, this ioctl might not be supported
            // Just warn and continue with use_mdm = 0
            warn!("DIAG_IOCTL_REMOTE_DEV ioctl failed, assuming use_mdm = 0");
            return Ok(0);
        }
    }
    Ok(use_mdm)
}

/// Try to create a DiagDevice, falling back to NewDiagDevice for newer chipsets
pub async fn create_diag_device_auto(configured_device: &Device) -> DiagResult<NewDiagDevice> {
    NewDiagDevice::new(configured_device).await
}
