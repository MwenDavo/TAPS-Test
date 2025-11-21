from beamngpy import BeamNGpy, Scenario, Vehicle

from sensor.taps import TAPS

BEAMNGTECHDIR = "C:\\Users\\David Gillig\\Downloads\\BeamNG.tech.v0.36.4.0"

bng = BeamNGpy('localhost', 25252, home=BEAMNGTECHDIR, quit_on_close=True)
bng.open(["tech/TAPS"],'-gfx', 'vk')

scenario = Scenario('automation_test_track', 'Test Track')
main_vehicle = Vehicle('main_vehicle', model='etk800', license='TEST')
scenario.add_vehicle(main_vehicle, pos=(487,178,132), cling=True)
scenario.make(bng)

bng.scenario.load(scenario)
bng.traffic.spawn(10)

bng.scenario.start()
main_vehicle.ai.set_mode('traffic')

#taps_v1 = TAPS("TAPS", bng, main_vehicle)

try:
   while True:
        pass
except KeyboardInterrupt:
    bng.close()