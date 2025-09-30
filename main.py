from beamngpy import BeamNGpy, Scenario, Vehicle

from sensor.taps import TAPS

BEAMNGTECHDIR = "C:\\Users\\David Gillig\\Downloads\\BeamNG.tech.v0.36.4.0"

bng = BeamNGpy('localhost', 25252, home=BEAMNGTECHDIR, quit_on_close=True)
bng.open(None,'-gfx', 'vk')

scenario = Scenario('automation_test_track', 'Test Track')
main_vehicle = Vehicle('main_vehicle', model='etk800', license='TEST', extensions=["tech/sensors","tech/techCore"])
scenario.add_vehicle(main_vehicle, pos=(487,178,132), cling=True)
scenario.make(bng)

bng.scenario.load(scenario)
bng.traffic.spawn(10)

bng.scenario.start()
main_vehicle.ai.set_mode('traffic')

try:
    taps_v1 = TAPS("TAPS", bng, main_vehicle)
except Exception as e:
    print(e)
    bng.close()

try:
   while True:
        #print(taps_v1.poll())
    pass
except KeyboardInterrupt:
    pass

bng.close()