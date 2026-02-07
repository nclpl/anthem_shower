"""Constants for the Anthem Shower integration."""

DOMAIN = "anthem_shower"

CONF_HOST = "host"
CONF_PIN = "pin"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 60

# RSA public key used by Anthem devices to encrypt the PIN
ANTHEM_RSA_PUBLIC_KEY_PEM = """-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAOBnPtJlU6y62vyrcHgqZPAlr+FM10BpUxBvRx5u0fXNEjXcda4y3WSU
2ECzf9HcmDU5r6fD2jiFPyTuXu7jY2qzAI7QME6eoaJd2q+QLKpcUVq5MTeFo9b6
zpZlGHUiiy0NrFdKPjD+UdPXi/t1oEKaj/loWiZ7p0P02paUoI41AgMBAAE=
-----END RSA PUBLIC KEY-----"""
