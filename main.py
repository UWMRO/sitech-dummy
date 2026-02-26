import asyncio
import telescope
# address 127.0.0.1
# o 127.0.0.1 8001 or telnet 127.0.0.1 8001

# runs the server
async def receive_commands(reader, writer):
    print("ready")
    
    while True:
        data = await reader.readline()
        data = data.decode()

        command, args = parse_command(data)
        try:
            eval(f"{command}(reader, writer, args)")
        except Exception as e:
            print(f"An error occurred: {type(e)}: {e}")
        
        # every command comes with scope's standard string output
        writer.write((str(scope) + "\n").encode())
        await writer.drain()

# returns a tuple of (command, arguments) given a sent command as written.
def parse_command(command: str) -> tuple[str, list[str]]:
    command_arr = command.split()
    return (command_arr[0], command_arr[1:])

# scope destination endpoint
# returns a standard string except the target's RA / Dec instead of the scope's
# currently returns the current state of the scope.
async def ReadScopeDestination(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    writer.write(str(scope).encode())
    await writer.drain()

# unparks the scope.
def UnPark(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    scope.park = False

# if no blinky mode on motors, defined park pos, moves to park and becomes parked.
def Park(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    scope.park = True

# if tracking, returns "You can't set park if you're tracking."
# if not, returns the standard string + ";_SetPark command successful"
async def SetPark(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    if scope.tracking:
        writer.write("You can't set park if you're tracking.".encode())
    else:
        writer.write(";_SetPark command successful".encode())
    await writer.drain()
        
# aborts any slews of the scope and disables tracking.
def Abort(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    scope.tracking = False

def MotorsToAuto(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    scope.blinky = False

def MotorsToBlinky(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    scope.blinky = True

# goto with tracking
def GoTo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    if(len(args) < 2):
        raise ValueError("RA, Dec must be provided.")
    
    RA = float(args[0])
    Dec = float(args[1])
    # SiTech takes RA in hours (1 hr = 15 degrees)
    scope.set_coords(RA, Dec)
    scope.tracking = True

    # debug logging
    print(f"DEBUG: Scope moved to {RA / 15} hours RA, {Dec} degrees.")

def GoToStop(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    GoTo(reader, writer, args)
    scope.tracking = False

# unclear whether altaz forces tracking to true, assuming that it does
def GoToAltAz(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    Az = float(args[0])
    Alt = float(args[1])
    scope.set_azalt(Az, Alt)
    scope.tracking = True

def GoToAltAzStop(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    GoToAltAz(reader, writer, args)
    scope.tracking = False

# stops or starts tracking at the given rate. if given 0.0 for either RA / Dec rate,
# scope will default to tracking at sidereal rate.
# format: SetTrackMode track rate RARate, DecRate
#       track: determines whether the telescope should track. 1 for yes, any other value for 0.
#       rate: 1 = use the following rates.  0 means track at the sidereal rate.
#       RARate: Right Ascension Rate (arc seconds per second).  A 0.0 will  track at the sidereal rate.
#       DecRate: Declination rate (arc seconds per second) A 0.0 will track the declination according to the telescope model and refraction.
# track, rate, RARate, DecRate
def SetTrackMode(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, args: list[str]):
    track = True if args[0] == "1" else False
    rate = float(args[1])
    RARate = float(args[2])
    DecRate = float(args[3])
    
    scope.tracking = track
    if rate == 1:
        if RARate == 0.0:
            scope.ra_tracking_sidereal = True
        else:
            scope.ra_tracking_sidereal = False
        if DecRate == 0.0:
            scope.dec_tracking_sidereal = True
        else:
            scope.dec_tracking_sidereal = False
            
async def main():
    server = await asyncio.start_server(receive_commands, host="127.0.0.1", port=8001)
    print("server started")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    scope = telescope.telescope()
    asyncio.run(main())