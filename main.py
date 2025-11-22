import asyncio
import telescope
# address 127.0.0.1
# o 127.0.0.1 8001

# runs the server
async def receive_commands(reader, writer):
    print("ready")
    
    while True:
        data = await reader.readline()
        data = data.decode().split()

        # single arg case:
        if len(data) == 1:
            command = data[0] + "()"

        # multiple arg case:
        elif len(data) > 1: 
            command = data[0] + "("
            
            for x in range(1, len(data)):
                command += data[x] + ","

            command = command[:-1] + ")"
        
        try:
            eval(command)
        except Exception as e:
            print(f"Exception Thrown: {e}")
        
        writer.write("response\n".encode())
        await writer.drain()



# scope destination endpoint
# returns a standard string except the target's RA / Dec instead of the scope's
def ReadScopeDestination():
    return 

# unparks the scope.
def UnPark():
    scope.park = False

# if no blinky mode on motors, defined park pos, moves to park and becomes parked.
def Park():
    scope.park = True

# if tracking, returns "You can't set park if you're tracking."
# if not, returns the standard string + ";_SetPark command successful"
async def SetPark(writer):
    if scope.tracking:
        writer.write("You can't set park if you're tracking.")
        await writer.drain()
    else:
        writer.write()
        
# aborts any slews of the scope and disables tracking.
def Abort():
    scope.tracking = False

def MotorsToAuto():
    scope.blinky = False

def MotorsToBlinky():
    scope.blinky = True

# goto with tracking
def GoTo(RA, Dec):
    scope.set_coords(RA, Dec)
    scope.tracking = True

def GoToStop(RA, Dec):
    GoTo(RA, Dec)
    scope.tracking = False

def GoToAltAz(Az, Alt):
    scope.set_azalt(Az, Alt)

# stops or starts tracking at the given rate. if given 0.0 for either RA / Dec rate,
# scope will default to tracking at sidereal rate.
def SetTrackMode(track, rate, RARate, DecRate):
    if track != 0:
        scope.tracking = False
    else:
        scope.tracking = True
        if rate == 1:
            if RARate == 0.0:
                RARate = "sidereal"
            if DecRate == 0.0:
                DecRate = "sidereal"
            
            print(f"Tracking at given rate: RA @ {RARate} arcsec / s, Dec @ {DecRate} arcsec / s")

async def main():
    server = await asyncio.start_server(receive_commands, host="127.0.0.1", port=8001)
    print("server started")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    scope = telescope.telescope()
    asyncio.run(main())