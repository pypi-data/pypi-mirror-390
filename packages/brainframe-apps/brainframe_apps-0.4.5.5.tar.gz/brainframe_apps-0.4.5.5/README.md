# brainframe-apps

Python CLI tool for managing BrainFrame video analytics server via REST APIs.

## Installation

```bash
pip install brainframe-apps
```

## Usage

```bash
brainframe_apps <command> [options]
```

### Commands

- `add-stream` - Add video stream
- `delete-stream` - Remove stream
- `list-stream` - List streams
- `start-analyzing` - Start stream analysis
- `stop-analyzing` - Stop stream analysis
- `capsule-control` - Manage AI capsules
- `identity-control` - Manage identities
- `user-control` - Manage users
- `license-control` - Manage licenses
- `get-zone-statuses` - Get zone status
- `process-image` - Process single image
- `load-settings` - Load configuration
- `save-settings` - Save configuration

### Example

```bash
brainframe_apps add-stream --server-url http://localhost --stream-url rtsp://camera.url
brainframe_apps list-stream
brainframe_apps start-analyzing --stream-name "Camera 1"
```

## Help

```bash
brainframe_apps <command> --help
```
