Run like this:

```
client = GuacamoleClient(
		"74.207.234.105",
		4822,
		{
				"protocol": "vnc",
				"size": [1024, 768, 96],
				"audio": [],
				"video": [],
				"image": [],
				"args": {
						"hostname": "hostname",
						"port": port,
						"username": "username",
						"password": "password",
				},
		},
		debug=True,
)
``
