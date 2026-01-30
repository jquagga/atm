# AwTrix Manager

A Python application that manages AwTrix WiFi clocks with automated day/night mode switching.

## Features

- Automated day/night mode scheduling
- Support for multiple clock devices
- Configurable settings via environment variables
- Docker containerized deployment
- Graceful error handling and logging
- Request timeouts to prevent hanging
- Signal handling for graceful shutdown

## Configuration

### Environment Variables

| Variable  | Description                                    | Default     |
| --------- | ---------------------------------------------- | ----------- |
| `HOSTS`   | Comma-separated list of clock IP addresses     | `127.0.0.1` |
| `TIM`     | Enable time display                            | `True`      |
| `DAT`     | Enable date display                            | `False`     |
| `HUM`     | Enable humidity display                        | `False`     |
| `TEMP`    | Enable temperature display                     | `False`     |
| `BAT`     | Enable battery display                         | `False`     |
| `TEFF`    | Transition effect (1-10)                       | `10`        |
| `SOM`     | Start week on Monday (False for Sunday)        | `True`      |
| `CEL`     | Use Celsius (False for Fahrenheit)             | `True`      |
| `TMODE`   | Time mode (0 = no calendar, 1 = with calendar) | `0`         |
| `TFORMAT` | Time format (strftime format)                  | `%H:%M`     |
| `WD`      | Show day of week                               | `False`     |

### Day/Night Mode Schedule

- **Night Mode**: 20:00 (8 PM) to 06:00 (6 AM)
- **Night Mode Features**:
  - Red time display color
  - Fixed low brightness (level 1)
  - Disabled auto-brightness
  - Disabled automatic app switching
- **Day Mode Features**:
  - White text color
  - Auto brightness enabled
  - Automatic app switching enabled
  - Weather overlay cleared

## Deployment

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Manual Docker Deployment

```bash
# Build the image
docker build -t atm .

# Run the container
docker run -d \
  --name atm \
  --restart unless-stopped \
  -v /etc/localtime:/etc/localtime:ro \
  -e HOSTS=10.0.1.39,10.0.1.246 \
  -e CEL=False \
  -e TFORMAT=%l:%M \
  atm
```

### Local Development

```bash
# Install dependencies using uv
uv sync

# Run the application
uv run python main.py
```

## Troubleshooting

### Clock Not Responding

Check the application logs:

```bash
docker logs atm
```

Common issues:

- **Connection Error**: Ensure the clocks are on the same network and accessible from the container
- **Timeout Error**: Check network connectivity and firewall settings
- **HTTP Error**: Verify the clock API is running and accessible

### Viewing Logs

The application uses structured logging with the following format:

```
YYYY-MM-DD HH:MM:SS - atm - LEVEL - message
```

Log levels:

- `INFO`: Normal operation messages
- `ERROR`: Errors during clock updates
- `WARNING`: Configuration issues

### Health Checks

The container includes a healthcheck that runs every 30 seconds. Check container health:

```bash
docker inspect --format='{{.State.Health.Status}}' atm
```

## Architecture

The application consists of three main components:

1. **Configuration**: Loads settings from environment variables
2. **Scheduler**: Uses the `schedule` library to manage day/night mode transitions
3. **Device Manager**: Sends HTTP requests to update clock settings

All HTTP requests include a 10-second timeout to prevent hanging.

## License

See LICENSE file for details.
