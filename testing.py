import asyncio

from flask import Flask
from bleak import discover, BleakClient

app = Flask(__name__)

__PWR_CHARACTERISTIC = "00001525-1212-efde-1523-785feabcd124"
__PWR_ON             = bytearray([0x01])
__PWR_STANDBY        = bytearray([0x00])

found_devices = []

@app.route("/all_on", methods=["POST"])
async def all_on():
	global found_devices
	count = 0
	for mac in found_devices:
		for i in range(0, 3):
			try:
				await set_power_state(mac, True)
				count += 1
				break
			except:
				print("Failed to send data")
	return {
		"success": True,
		"device_count": count
	}

@app.route("/all_off", methods=["POST"])
async def all_off():
	global found_devices
	count = 0
	print(found_devices)
	for mac in found_devices:
		for i in range(0, 3):
			try:
				await set_power_state(mac, False)
				count += 1
				break
			except:
				print("Failed to send data")
	return {
		"success": True,
		"device_count": count
	}

async def discover_devices():
	global found_devices
	print("Running scan...")
	lh_macs = []
	devices = await discover()
	for d in devices:
		if d.name == None:
			continue
		if d.name.find("LHB-") != 0:
			continue
		print("Found Lighthouse with address " + d.address + " named "+ d.name)
		lh_macs.append(d.address)
	found_devices = lh_macs

	print("Scan complete. Found " + str(len(found_devices)) + " devices")

async def set_power_state(mac, state):
	print("Attempting to set the power state of " + mac)
	client = BleakClient(mac)
	await client.connect()
	print("Connected to " + str(mac))


	to_send = None
	if state == True:
		to_send = __PWR_ON
	else:
		to_send = __PWR_STANDBY

	print("Sending " + str(to_send) + " to device " + str(mac))
	await client.write_gatt_char(__PWR_CHARACTERISTIC, to_send)

	await client.disconnect()
	print("Disconnected from " + str(mac))

def perform_scan():
	print("perform_scan")
	loop = asyncio.get_event_loop()
	coroutine = discover_devices()
	loop.run_until_complete(coroutine)

if __name__ == "__main__":
	perform_scan()

	app.run(debug=False, host="0.0.0.0", port=8030)