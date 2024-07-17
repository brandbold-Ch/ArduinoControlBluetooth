from bleak import BleakClient


async def send_command(command):
    client = BleakClient("98:DA:BE:01:8D:A7")
    try:
        await client.connect()
        print("Conectado al bluetooth")

        await client.write_gatt_char(
            "0000FFE2-0000-1000-8000-00805F9B34FB",
            bytearray(command.encode()), True
        )
        print(f"Comando enviado: {command}")

        response = await client.read_gatt_char("0000FFE1-0000-1000-8000-00805F9B34FB")
        print(f"Respuesta recibida: {response.decode('utf-8')[0]}")
        return response.decode("utf-8")[0]

    except Exception as e:
        print(f"Error al enviar comando: {e}")

    finally:
        await client.disconnect()
